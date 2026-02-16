import os
import json
import re
from datetime import datetime
from typing import TypedDict, Annotated, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode

from app.agents.tools.sql_rewrite_tool import rewrite_sql
from app.agents.tools.neo4j_tool import run_cypher
from app.agents.middleware.human_approval import requires_approval
from app.config import OPENAI_API_KEY
from app.memory.sqlite_store import save_message, load_messages

# --- 1. SYSTEM PROMPT (The "Rules of Engagement") ---
SYSTEM_PROMPT = """
You are a senior Data Warehouse Architect and Orchestrator. 
Your goal is to help users understand metadata, build SQL, and manage files.

CORE CAPABILITIES:
1. SCHEMA CHAT: Use 'get_database_schema' to explain tables and relationships to the user.
2. SQL GENERATION: Use 'process_sql_generation' to create safe, optimized SQL.
3. FILE MANAGEMENT: Use 'create_document' or 'edit_file' to save your work or update specs.

GUIDELINES:
- Always prioritize technical accuracy.
- If the user asks for SQL, you MUST run it through 'process_sql_generation'.
- Be conversational. If you call a tool, explain what the tool found or did.
- If you aren't sure about a table name, ask the user or check the schema tool first.
"""
# --- 1. DEFINE AGENT STATE ---
class AgentState(TypedDict):
    # Keep appending messages across nodes. Without this reducer, each node
    # overwrites state and can send invalid tool-role sequences to OpenAI.
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str
    session_id: str
    intent: str
    generated_sql: str
    requires_approval: bool
    sql_filename: str

# --- 2. DEFINE TOOLS ---
@tool
def create_document(filename: str, content: str):
    """Creates a new text or markdown document on the server."""
    os.makedirs("./docs", exist_ok=True)
    with open(f"./docs/{filename}", "w") as f:
        f.write(content)
    return f"Document {filename} created successfully."

@tool
def edit_file(filename: str, search_text: str, replace_text: str):
    """Edits an existing file by replacing a specific string."""
    if not os.path.exists(filename):
        return "File not found."
    with open(filename, "r") as f:
        data = f.read()
    new_data = data.replace(search_text, replace_text)
    with open(filename, "w") as f:
        f.write(new_data)
    return f"File {filename} updated."

@tool
def process_sql_generation(raw_sql: str):
    """Validates and rewrites SQL for safety. Use this when the user wants SQL."""
    # Ensure raw_sql isn't empty or just markdown
    clean_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
    safe_sql = rewrite_sql(clean_sql)
    return {
        "safe_sql": safe_sql, 
        "approval_needed": requires_approval(safe_sql)
    }

@tool
def get_database_schema(table_name: str):
    """Fetches active table schema (columns, datatypes, keys) from metadata graph."""
    try:
        query = """
        MATCH (t:Table)-[:HAS_VERSION]->(v:TableVersion {active:true})-[:HAS_COLUMN]->(c:ColumnVersion {active:true})
        WHERE t.id = $table_name OR t.name = $table_name OR t.id ENDS WITH ('.' + $table_name)
        RETURN t.id AS table_id,
               v.id AS version_id,
               collect({
                   name: c.name,
                   datatype: c.datatype,
                   is_pk: coalesce(c.is_pk, false),
                   is_fk: coalesce(c.is_fk, false)
               }) AS columns
        LIMIT 1
        """
        rows = run_cypher(query=query, table_name=table_name)
        if not rows:
            return {
                "table_name": table_name,
                "found": False,
                "columns": [],
                "message": "No active schema found for this table."
            }
        row = rows[0]
        return {
            "table_name": row.get("table_id", table_name),
            "version": row.get("version_id"),
            "found": True,
            "columns": row.get("columns", [])
        }
    except Exception as e:
        return {
            "table_name": table_name,
            "found": False,
            "columns": [],
            "error": str(e)
        }

# --- 3. CONFIGURE LLM & GRAPH ---
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=KEY,
)

tools = [create_document, edit_file, process_sql_generation, get_database_schema]
model_with_tools = llm.bind_tools(tools)

def _extract_sql_from_text(text: str) -> str:
    if not text:
        return ""

    # 1) JSON payload style: {"final_sql":"..."}
    json_sql = re.search(r'"final_sql"\s*:\s*"((?:\\.|[^"\\])*)"', text, re.IGNORECASE | re.DOTALL)
    if json_sql:
        try:
            return bytes(json_sql.group(1), "utf-8").decode("unicode_escape").strip()
        except Exception:
            return json_sql.group(1).strip()

    # 2) SQL code fence
    for block in re.findall(r"```(?:sql)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL):
        if re.search(r"\b(select|create|with|insert)\b", block, re.IGNORECASE):
            return block.strip()

    # 3) Freeform fallback
    create_stmt = re.search(r"(CREATE\s+TABLE[\s\S]*?;)", text, re.IGNORECASE)
    if create_stmt:
        return create_stmt.group(1).strip()

    return ""

def _looks_like_sql(text: str) -> bool:
    if not text:
        return False

    lowered = text.strip().lower()
    placeholders = {
        "the full sql statement",
        "final sql",
        "sql statement",
        "proposed sql",
    }
    if lowered in placeholders:
        return False

    return bool(
        re.search(r"\b(select|create|with|insert)\b", text, re.IGNORECASE)
        and re.search(r"\b(from|as)\b", text, re.IGNORECASE)
    )

def _extract_column_name(question: str) -> str:
    if not question:
        return ""
    patterns = [
        r"schema\s+for\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"type\s+of\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"datatype\s+of\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def _find_latest_sql(messages: List[BaseMessage]) -> str:
    for msg in reversed(messages):
        content = getattr(msg, "content", "")
        if not isinstance(content, str):
            continue
        sql_text = _extract_sql_from_text(content)
        if sql_text:
            return sql_text
    return ""

def _infer_column_schema(sql_text: str, column_name: str) -> str:
    if not sql_text or not column_name:
        return ""

    col = re.escape(column_name)
    rules = [
        (rf"COUNT\s*\([^)]*\)\s+AS\s+{col}\b", "BIGINT"),
        (rf"SUM\s*\([^)]*\)\s+AS\s+{col}\b", "DECIMAL/NUMERIC"),
        (rf"AVG\s*\([^)]*\)\s+AS\s+{col}\b", "DOUBLE/DECIMAL"),
        (rf"MIN\s*\([^)]*\)\s+AS\s+{col}\b", "Same as source column datatype"),
        (rf"MAX\s*\([^)]*\)\s+AS\s+{col}\b", "Same as source column datatype"),
    ]
    for pattern, dtype in rules:
        if re.search(pattern, sql_text, re.IGNORECASE):
            return dtype
    # If the alias exists but not from a known aggregate, assume passthrough.
    if re.search(rf"\bAS\s+{col}\b", sql_text, re.IGNORECASE):
        return "Same as source column datatype"
    return ""

def _split_select_expressions(select_clause: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    depth = 0
    for ch in select_clause:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(ch)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts

def _infer_all_column_schemas(sql_text: str) -> List[dict]:
    if not sql_text:
        return []

    select_match = re.search(r"\bSELECT\b([\s\S]*?)\bFROM\b", sql_text, re.IGNORECASE)
    if not select_match:
        return []

    select_clause = select_match.group(1)
    result: List[dict] = []
    for expr in _split_select_expressions(select_clause):
        alias_match = re.search(r"\bAS\s+([a-zA-Z_][a-zA-Z0-9_]*)\b", expr, re.IGNORECASE)
        if alias_match:
            col_name = alias_match.group(1)
        else:
            # Handle simple passthrough like "customer_id"
            bare = re.match(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*$", expr)
            if not bare:
                continue
            col_name = bare.group(1)

        result.append(
            {
                "column": col_name,
                "inferred_datatype": _infer_column_schema(sql_text, col_name) or "Unknown (needs source schema)",
            }
        )
    return result

def route_intent(state: AgentState):
    intent = state.get("intent", "chat")
    if intent in ("sql_write", "sql_rewrite"):
        return "sql_pipeline"
    if intent == "schema_question":
        return "schema_pipeline"
    return "agent"

def detect_intent(state: AgentState):
    text = (state.get("user_input") or "").lower()

    if ("schema" in text and "column" in text) or ("schema for" in text) or ("datatype of" in text) or ("type of" in text):
        intent = "schema_question"
    elif ("write the sql file" in text) or ("final_sql" in text) or ("proposed sql" in text):
        intent = "sql_write"
    elif ("rewrite" in text and "sql" in text):
        intent = "sql_rewrite"
    else:
        intent = "chat"

    return {"intent": intent}

def sql_pipeline(state: AgentState):
    user_input = state.get("user_input", "")
    session_id = state.get("session_id", "session")
    raw_sql = _extract_sql_from_text(user_input)
    intent = state.get("intent", "sql_write")

    # For rewrite requests, allow using prior generated SQL when user does not paste it again.
    if not raw_sql and intent == "sql_rewrite":
        raw_sql = _find_latest_sql(state.get("messages", []))

    if not raw_sql or not _looks_like_sql(raw_sql):
        return {
            "messages": [AIMessage(content="I could not find valid SQL. Please provide executable SQL (not placeholders like `The full SQL statement`).")],
            "generated_sql": "",
            "requires_approval": False,
            "sql_filename": "",
        }

    sql_result = process_sql_generation.invoke({"raw_sql": raw_sql})
    safe_sql = sql_result.get("safe_sql", "")
    approval = bool(sql_result.get("approval_needed", False))

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{session_id}_generated_{timestamp}.sql"
    create_document.invoke({"filename": filename, "content": safe_sql + "\n"})

    reply = (
        f"SQL generated and saved to `docs/{filename}`.\n\n"
        f"Schema hint: `total_orders` from `COUNT(...)` is usually `BIGINT`.\n\n"
        f"```sql\n{safe_sql}\n```"
    )
    return {
        "messages": [AIMessage(content=reply)],
        "generated_sql": safe_sql,
        "requires_approval": approval,
        "sql_filename": filename,
    }

def schema_pipeline(state: AgentState):
    question = state.get("user_input", "")
    column = _extract_column_name(question)
    latest_sql = _find_latest_sql(state.get("messages", []))

    if latest_sql and ("all schema" in question.lower() or "all schemas" in question.lower() or "all columns" in question.lower()):
        columns = _infer_all_column_schemas(latest_sql)
        if columns:
            lines = ["Inferred schema for columns in the latest SQL:"]
            for c in columns:
                lines.append(f"- {c['column']}: {c['inferred_datatype']}")
            return {"messages": [AIMessage(content="\n".join(lines))]}

    if column and latest_sql:
        inferred_type = _infer_column_schema(latest_sql, column)
        if inferred_type:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            f"`{column}` is a derived column from your generated SQL.\n"
                            f"Expected datatype: `{inferred_type}`.\n"
                            f"Reason: it is derived using an aggregate expression."
                        )
                    )
                ]
            }

    return {
        "messages": [
            AIMessage(
                content=(
                    "I can answer schema precisely if you share the table/column reference "
                    "(for example: `ODP.sales.orders.order_amount`) or provide the generated SQL."
                )
            )
        ]
    }

def call_model(state: AgentState):
    # The fix for "messages role tool" error: 
    # Ensure the history is consistent before calling OpenAI
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def route_logic(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("detect_intent", detect_intent)
workflow.add_node("sql_pipeline", sql_pipeline)
workflow.add_node("schema_pipeline", schema_pipeline)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.set_entry_point("detect_intent")
workflow.add_conditional_edges("detect_intent", route_intent)
workflow.add_conditional_edges("agent", route_logic)
workflow.add_edge("tools", "agent")
workflow.add_edge("sql_pipeline", END)
workflow.add_edge("schema_pipeline", END)

app = workflow.compile()

# --- 4. THE REWRITTEN RUNNER ---
def run_agent(session_id: str, user_input: str, use_history: bool = True, persist_history: bool = True):
    try:
        history = []
        if use_history:
            # Expected format from load_messages: List[Tuple(role, content)]
            history = load_messages(session_id)
        
        # 2. Build CLEAN history
        # We start with the System Message to define the agent's personality
        initial_messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Convert stored history into LangChain message objects
        for role, content in history:
            if role == "user":
                initial_messages.append(HumanMessage(content=str(content)))
            elif role == "assistant":
                # IMPORTANT: We only pass the text 'content'. 
                # This strips old tool_calls and prevents the "role: tool" sequence error.
                if content: # Only add if there is actual text
                    initial_messages.append(AIMessage(content=str(content)))
        
        # 3. Add the CURRENT user input (Outside the loop!)
        initial_messages.append(HumanMessage(content=user_input))
        
        # 4. Invoke the Graph
        # LangGraph will handle the loop between the LLM and the Tools
        final_state = app.invoke(
            {
                "messages": initial_messages,
                "user_input": user_input,
                "session_id": session_id,
            }
        )
        
        # 5. Extraction Logic
        # The last message in the state is the final response from the assistant
        last_msg = final_state["messages"][-1]
        chat_reply = last_msg.content if isinstance(last_msg.content, str) else json.dumps(last_msg.content)
        
        generated_sql = final_state.get("generated_sql", "")
        approval_flag = final_state.get("requires_approval", False)

        # 6. Extract Tool Output (Specifically for SQL generation)
        # We look through the messages in the final state for ToolMessages 
        # that contain our 'safe_sql' payload.
        for msg in final_state["messages"]:
            if isinstance(msg, ToolMessage):
                try:
                    # Tool outputs from ToolNode are usually JSON strings
                    data = json.loads(msg.content)
                    if isinstance(data, dict) and "safe_sql" in data:
                        generated_sql = data["safe_sql"]
                        approval_flag = data.get("approval_needed", False)
                except (json.JSONDecodeError, TypeError):
                    # Not a JSON tool response or not the one we are looking for
                    continue

        # 7. Persistence
        # Save the turn to the database for the next interaction
        if persist_history:
            save_message(session_id, "user", user_input)
            save_message(session_id, "assistant", chat_reply)

        return {
            "status": "completed",
            "chat_reply": chat_reply,
            "sql": generated_sql,
            "requires_approval": approval_flag
        }

    except Exception as e:
        # Log the actual error to your terminal for debugging
        print(f"CRITICAL AGENT ERROR: {str(e)}")
        
        # Return a clean error object so the frontend doesn't crash
        return {
            "status": "error",
            "chat_reply": f"I encountered an error while processing your request: {str(e)}",
            "sql": "",
            "requires_approval": False
        }
