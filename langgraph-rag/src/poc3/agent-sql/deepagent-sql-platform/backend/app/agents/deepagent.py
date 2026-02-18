import os
import json
import re
from datetime import datetime
from typing import TypedDict, Annotated, List, Dict, Any

import sqlglot
from sqlglot import exp

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END, add_messages

from app.agents.tools.sql_rewrite_tool import rewrite_sql
from app.agents.tools.neo4j_tool import run_cypher
from app.agents.middleware.human_approval import requires_approval
from app.config import OPENAI_API_KEY
from app.memory.sqlite_store import save_message, load_messages
from app.memory.session_context import load_context, save_context

# =========================================================
# 1️⃣ SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are a Senior Data Warehouse Architect.

Rules:
- Never hallucinate tables or columns.
- Always validate against provided GRAPH CONTEXT.
- Prefer explicit JOIN conditions.
- If unsure about schema, ask or check schema tool.
- Maintain conversation continuity.
"""

# =========================================================
# 2️⃣ SESSION STATE
# =========================================================

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str
    session_id: str
    intent: str
    last_generated_sql: str
    last_validation_errors: List[str]
    last_intent: str
    last_schema_lookup: Dict[str, Any]
    business_context: Dict[str, Any]
    orchestration_status: Dict[str, str]

# =========================================================
# 3️⃣ LLM
# =========================================================

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key="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"
)

# =========================================================
# 4️⃣ INTENT ROUTER
# =========================================================

def detect_intent(state: AgentState):
    text = (state.get("user_input") or "").lower()
    if any(word in text for word in ["schema", "datatype", "structure"]):
        intent = "schema"
    elif any(word in text for word in ["business", "meaning", "definition"]):
        intent = "business"
    elif any(word in text for word in ["modify", "change", "update", "add", "remove"]):
        intent = "sql_modify"
    elif any(word in text for word in ["sql", "select", "generate", "count", "sum", "group by", "join", "total"]):
        intent = "sql_generate"
    else:
        intent = "chat"
    return {"intent": intent, "last_intent": intent}

def route_intent(state: AgentState):
    mapping = {
        "sql_generate": "orchestrator",
        "sql_modify": "orchestrator",
        "schema": "orchestrator",
        "business": "orchestrator",
        "chat": "orchestrator",
    }
    return mapping.get(state["intent"], "orchestrator")

# =========================================================
# 5️⃣ SQL UTILITIES
# =========================================================

def extract_sql_from_text(text: str) -> str:
    blocks = re.findall(r"```(?:sql)?\s*(.*?)```", text, re.I | re.S)
    if blocks:
        return blocks[0].strip()
    match = re.search(r"(SELECT[\s\S]+?;)", text, re.I)
    return match.group(1).strip() if match else ""

def extract_sql_metadata(sql_text: str):
    try:
        parsed = sqlglot.parse_one(sql_text)
    except Exception:
        return set(), set()
    tables = {t.name for t in parsed.find_all(exp.Table)}
    columns = {c.name for c in parsed.find_all(exp.Column)}
    return tables, columns

def resolve_table_name(table_name: str, graph_context: dict) -> str | None:
    if table_name in graph_context:
        return table_name
    for full_name in graph_context.keys():
        if full_name.split(".")[-1] == table_name:
            return full_name
    return None

def validate_sql_against_graph(sql_text: str, graph_context: Dict[str, Any]):
    errors = []
    tables, columns = extract_sql_metadata(sql_text)
    resolved_tables = {}

    for table in tables:
        resolved = resolve_table_name(table, graph_context)
        if not resolved:
            errors.append(f"Table '{table}' not found in graph context.")
        else:
            resolved_tables[table] = resolved

    for column in columns:
        found = any(
            column == col.get("name")
            for table_schema in graph_context.values()
            for col in table_schema.get("columns", [])
        )
        if not found:
            errors.append(f"Column '{column}' not found in graph context.")

    return errors, resolved_tables

# =========================================================
# 6️⃣ SESSION STATE MANAGER
# =========================================================

def update_session_state(session_id: str, updates: Dict[str, Any]):
    context = load_context(session_id) or {}
    context.setdefault("compiler_state", {})
    context.setdefault("orchestration_status", {})
    context["compiler_state"].update(updates)
    context["orchestration_status"].update({k: "completed" for k in updates.keys()})
    save_context(session_id, context)

# =========================================================
# 7️⃣ ORCHESTRATOR NODE
# =========================================================

def orchestrator(state: AgentState):
    # Route to appropriate pipeline
    intent = state["intent"]
    result = {}
    if intent in ["sql_generate", "sql_modify"]:
        result = sql_pipeline(state)
    elif intent == "schema":
        result = schema_pipeline(state)
    elif intent == "business":
        result = business_pipeline(state)
    elif intent == "chat":
        result = chat_pipeline(state)
    # Update orchestration status
    update_session_state(state["session_id"], {intent: "completed"})
    return result

# =========================================================
# 8️⃣ SQL PIPELINE (CSV aware)
# =========================================================

def sql_pipeline(state: AgentState):
    session_id = state["session_id"]
    context_data = load_context(session_id) or {}
    graph_context = context_data.get("graph_context", {})
    compiler_state = context_data.get("compiler_state", {})
    previous_sql = compiler_state.get("last_generated_sql")
    business_spec = context_data.get("business_spec", {})

    # Include CSV content if available
    csv_data = context_data.get("uploaded_csv", {})  # expects dict: table -> list of rows
    csv_summary = []
    for table, rows in csv_data.items():
        if rows:
            sample = rows[:5]  # first 5 rows
            csv_summary.append(f"Table: {table}\nSample Rows: {json.dumps(sample, indent=2)}")
    csv_summary_text = "\n\n".join(csv_summary) if csv_summary else "No CSV data uploaded."

    # Build prompt strictly from business spec
    if business_spec:
        prompt = f"""
You are a Senior Data Warehouse Architect.

Business Request: Generate SQL based on this business specification.

Business Spec:
{json.dumps(business_spec, indent=2)}

CSV Data (sample rows):
{csv_summary_text}

Source Table Schemas:
{json.dumps(graph_context, indent=2)}

Rules:
1. Only use columns defined in the business spec.
2. Apply aggregate functions as specified.
3. Output a valid SQL query to create the target table.
4. Return SQL only inside ```sql``` block.
"""
    # If user explicitly wants to modify previous SQL
    elif previous_sql and "modify" in state["user_input"].lower():
        prompt = f"""
Previous SQL:
{previous_sql}

User wants:
{state['user_input']}

Return ONLY SQL inside ```sql``` block.
"""
    else:
        # Fallback: simple SQL generation based on user_input description
        prompt = f"""
Generate SQL using GRAPH CONTEXT and CSV samples.

CSV Data:
{csv_summary_text}

Business Request:
{state['user_input']}

Return ONLY SQL inside ```sql``` block.
"""

    # Call LLM
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT + "\n\nGRAPH CONTEXT:\n" + json.dumps(graph_context, indent=2)),
        HumanMessage(content=prompt)
    ])

    raw_sql = extract_sql_from_text(response.content)
    if not raw_sql:
        return {"messages": [AIMessage(content="⚠️ Could not generate SQL. Please clarify.")]}

    safe_sql = rewrite_sql(raw_sql)

    # Validation loop: fix table/column issues
    for _ in range(2):
        errors, resolved_tables = validate_sql_against_graph(safe_sql, graph_context)
        for short, full in resolved_tables.items():
            if short != full:
                safe_sql = re.sub(rf"\b{short}\b", full, safe_sql)
        if not errors:
            break
        fix_prompt = f"""
SQL has validation errors:
{errors}

Fix using GRAPH CONTEXT.
Return ONLY corrected SQL inside ```sql``` block.
"""
        fix_response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT + "\n\nGRAPH CONTEXT:\n" + json.dumps(graph_context, indent=2)),
            HumanMessage(content=fix_prompt)
        ])
        corrected_sql = extract_sql_from_text(fix_response.content)
        if not corrected_sql:
            break
        safe_sql = rewrite_sql(corrected_sql)

    final_errors, _ = validate_sql_against_graph(safe_sql, graph_context)
    if final_errors:
        return {"messages": [AIMessage(content=f"⚠️ Unable to fix SQL automatically:\n{final_errors}")]}

    # Save SQL
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{session_id}_{timestamp}.sql"
    os.makedirs("./docs", exist_ok=True)
    with open(f"./docs/{filename}", "w") as f:
        f.write(safe_sql)

    # Update session state
    update_session_state(session_id, {
        "last_generated_sql": safe_sql,
        "last_validation_errors": [],
        "last_sql_file": filename,
        "approved": not requires_approval(safe_sql)
    })

    return {"messages": [AIMessage(content=f"✅ SQL generated and saved as {filename}:\n```sql\n{safe_sql}\n```")]}

# =========================================================
# 9️⃣ SCHEMA PIPELINE (supports column queries)
# =========================================================

def schema_pipeline(state: AgentState):
    session_id = state["session_id"]
    user_input = state["user_input"].lower()
    context_data = load_context(session_id) or {}
    graph_context = context_data.get("graph_context", {})

    # Column-specific query
    col_match = re.search(r"(?:column|field|attribute|schema of)\s+(\w+)", user_input)
    if col_match:
        col_name = col_match.group(1)
        for table, schema in graph_context.items():
            for col in schema.get("columns", []):
                if col.get("name") == col_name:
                    return {"messages": [AIMessage(content=json.dumps({
                        "table": table,
                        "column": col_name,
                        "type": col.get("datatype"),
                        "primary_key": col.get("primary_key", False)
                    }, indent=2))]}
        return {"messages": [AIMessage(content=f"⚠️ Column '{col_name}' not found in graph context.")]}

    # Table-level query fallback
    table_match = re.search(r"schema\s+for\s+(\w+)", user_input)
    if table_match:
        table_name = table_match.group(1)
        query = """
        MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
        WHERE t.name = $table
        RETURN t.name as table,
               collect({name:c.name, datatype:c.datatype}) as columns
        """
        rows = run_cypher(query=query, table=table_name)
        update_session_state(session_id, {"last_schema_lookup": rows})
        return {"messages": [AIMessage(content=json.dumps(rows, indent=2))]}

    return {"messages": [AIMessage(content="⚠️ Please specify a column or table name.")]}

# =========================================================
# 10️⃣ BUSINESS PIPELINE
# =========================================================

def business_pipeline(state: AgentState):
    session_id = state["session_id"]
    context_data = load_context(session_id) or {}
    business_context = context_data.get("business_spec", {})
    return {"messages": [AIMessage(content=json.dumps(business_context, indent=2))]}

# =========================================================
# 11️⃣ CHAT PIPELINE
# =========================================================

def chat_pipeline(state: AgentState):
    session_id = state["session_id"]
    context_data = load_context(session_id) or {}
    graph_context = context_data.get("graph_context", {})
    compiler_state = context_data.get("compiler_state", {})

    system_message = SystemMessage(
        content=SYSTEM_PROMPT +
                "\n\nGRAPH CONTEXT:\n" + json.dumps(graph_context, indent=2) +
                "\n\nCOMPILER MEMORY:\n" + json.dumps(compiler_state, indent=2)
    )

    filtered_messages = [msg for msg in state["messages"] if not isinstance(msg, SystemMessage)]
    messages = [system_message] + filtered_messages
    response = llm.invoke(messages)
    return {"messages": [response]}

# =========================================================
# 12️⃣ WORKFLOW
# =========================================================

workflow = StateGraph(AgentState)
workflow.add_node("detect_intent", detect_intent)
workflow.add_node("orchestrator", orchestrator)
workflow.add_node("sql_pipeline", sql_pipeline)
workflow.add_node("schema_pipeline", schema_pipeline)
workflow.add_node("business_pipeline", business_pipeline)
workflow.add_node("chat_pipeline", chat_pipeline)

workflow.set_entry_point("detect_intent")
workflow.add_conditional_edges("detect_intent", route_intent)
workflow.add_edge("orchestrator", END)
app = workflow.compile()

# =========================================================
# 13️⃣ RUNNER
# =========================================================

def run_agent(session_id: str, user_input: str):
    try:
        history = load_messages(session_id)
        context_data = load_context(session_id) or {}
        graph_context = context_data.get("graph_context", {})

        initial_messages = [SystemMessage(content=SYSTEM_PROMPT + "\n\nGRAPH CONTEXT:\n" + json.dumps(graph_context, indent=2))]
        for role, content in history:
            if role == "user":
                initial_messages.append(HumanMessage(content=str(content)))
            elif role == "assistant":
                initial_messages.append(AIMessage(content=str(content)))
        initial_messages.append(HumanMessage(content=user_input))

        final_state = app.invoke({
            "messages": initial_messages,
            "user_input": user_input,
            "session_id": session_id,
        })

        last_msg = final_state["messages"][-1]
        chat_reply = last_msg.content

        save_message(session_id, "user", user_input)
        save_message(session_id, "assistant", chat_reply)

        return {"status": "completed", "chat_reply": chat_reply}

    except Exception as e:
        return {"status": "error", "chat_reply": str(e)}
