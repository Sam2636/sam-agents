from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.deepagent import run_agent
from app.config import SESSION_UPLOADS_DIR
from pathlib import Path
import logging
import pandas as pd
from typing import Set
import os
from mcp.client.streamable_http import streamablehttp_client

# ---------------------------------------------------
# Router + Logging
# ---------------------------------------------------

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from mcp import ClientSession
from mcp.client.sse import sse_client
# ---------------------------------------------------
# MCP CONFIG
# ---------------------------------------------------
MCP_URL = os.getenv("MCP_URL", "http://localhost:8003/sse")

import json # Ensure this is imported at the top

async def fetch_table_schema(table_name: str):
    try:
        async with sse_client(MCP_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool(
                    "get_table_schema",
                    arguments={"table_name": table_name}
                )
                
                if not result.content:
                    return {}

                # The content is a string; we must parse it to use .get() later
                raw_text = result.content[0].text
                #logger.info(f"Raw MCP response for table {table_name}: {raw_text}")
                try:
                    parsed = json.loads(raw_text)
                    logger.info(f"Parsed MCP response for table {table_name}: {parsed}")
                    return parsed
                except json.JSONDecodeError:
                    # If the tool returned a string that isn't JSON, 
                    # handle it or return the raw string
                    #.warning(f"MCP returned non-JSON text: {raw_text}")    
                    return {"raw_output": raw_text}

    except Exception as e:
        #logger.error(f"MCP call failed for table {table_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch schema from MCP for table: {table_name}"
        )
# ---------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str

def _tables_from_session_csv(session_id: str) -> Set[str]:
    session_path = Path(SESSION_UPLOADS_DIR) / session_id
    if not session_path.exists():
        return set()

    source_tables: Set[str] = set()
    for file_path in session_path.glob("*.csv"):
        try:
            df = pd.read_csv(file_path)
        except Exception:
            continue

        # Source lineage tables in metadata CSV
        if "source_tables" in df.columns:
            for val in df["source_tables"].dropna():
                source_tables.update({t.strip() for t in str(val).split(",") if t.strip()})

        # Also include target table names when available
        if {"layer", "schema", "table_name"}.issubset(df.columns):
            for _, row in df[["layer", "schema", "table_name"]].dropna().drop_duplicates().iterrows():
                source_tables.add(f"{row['layer']}.{row['schema']}.{row['table_name']}")

    return source_tables

@router.post("/")
async def chat(req: ChatRequest):
    msg = (req.message or "").lower()
    asks_all_schema = ("schema" in msg) and ("all" in msg)
    if asks_all_schema:
        tables = _tables_from_session_csv(req.session_id)
        if not tables:
            return {
                "status": "completed",
                "chat_reply": "No tables found in uploaded CSV metadata for this session.",
                "sql": "",
                "requires_approval": False,
            }

        schema_lines = []
        for table in sorted(tables):
            schema_data = await fetch_table_schema(table)
            cols = schema_data.get("columns", []) if isinstance(schema_data, dict) else []
            if cols:
                schema_lines.append(f"- {table}: {cols}")
            else:
                schema_lines.append(f"- {table}: schema not found from MCP")

        return {
            "status": "completed",
            "chat_reply": "Schemas from MCP:\n" + "\n".join(schema_lines),
            "sql": "",
            "requires_approval": False,
        }

    return run_agent(req.session_id, req.message)

# ---------------------------------------------------
# Plan Builder (Graph-Enforced)
# ---------------------------------------------------
@router.post("/plan/{session_id}")
async def build_plan_from_session(session_id: str):
    session_path = Path(SESSION_UPLOADS_DIR) / session_id

    if not session_path.exists():
        raise HTTPException(status_code=404, detail="Session folder not found.")

    csv_files = list(session_path.glob("*.csv"))
    if not csv_files:
        raise HTTPException(status_code=404, detail="No CSV files found.")

    # Initialize outside the loop to accumulate data across ALL files
    all_metadata_blocks = []
    source_tables: Set[str] = set()

    # 1. PROCESS ALL CSV FILES
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            continue

        required_columns = [
            "layer", "schema", "table_name", "column_name",
            "datatype", "transformation_logic",
            "source_tables", "source_columns"
        ]

        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"File {file_path.name} is missing columns: {missing}"
            )

        # Extract unique source tables for MCP lookups
        for val in df["source_tables"].dropna():
            tables = [t.strip() for t in str(val).split(",") if t.strip()]
            source_tables.update(tables)

        # Group by target table to build structured prompt blocks
        grouped = df.groupby(["layer", "schema", "table_name"])
        for (layer, schema, table), group_df in grouped:
            columns_info = []
            for _, row in group_df.iterrows():
                columns_info.append(
                    f"- Column: {row['column_name']}\n"
                    f"  Logic: {row['transformation_logic']}\n"
                    f"  Source: {row['source_tables']}.{row['source_columns']}"
                )

            all_metadata_blocks.append(
                f"TARGET TABLE: {layer}.{schema}.{table}\n"
                f"COLUMNS TO GENERATE:\n" + "\n".join(columns_info)
            )

    # 2. VALIDATE SOURCE TABLES
    if not source_tables:
        raise HTTPException(
            status_code=400,
            detail="No source tables found in metadata. Cannot validate against Graph Schema."
        )

    # 3. FETCH MCP GRAPH SCHEMA
    graph_context_blocks = []
    for table in source_tables:
        schema_data = await fetch_table_schema(table)
        
        # We handle missing schemas gracefully or strictly depending on needs
        if schema_data:
            graph_context_blocks.append(
                f"GRAPH SCHEMA FOR TABLE: {table}\n"
                f"Columns: {schema_data.get('columns', [])}\n"
                f"Dependencies: {schema_data.get('dependencies', [])}"
            )
        else:
            logger.warning(f"No schema found for {table}, but continuing...")

    if not graph_context_blocks:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve any schema context from MCP."
        )

    # 4. CONSTRUCT FINAL ARCHITECT PROMPT
    final_metadata = "\n\n---\n\n".join(all_metadata_blocks)
    final_graph = "\n\n---\n\n".join(graph_context_blocks)

    instruction_prompt = f"""You are a senior Data Warehouse Architect.

### OBJECTIVE
1. Interpret transformation logic and generate valid SQL CREATE TABLE statements.
2. Apply GROUP BY logic where aggregates (SUM, COUNT, etc.) are present.
3. Use the GRAPH SCHEMA CONTEXT to validate that source columns and joins actually exist.
4. If a column in the METADATA is missing from the GRAPH SCHEMA, flag it as an error instead of generating SQL.

### METADATA SPECIFICATION
{final_metadata}

### GRAPH SCHEMA CONTEXT
{final_graph}

### OUTPUT FORMAT
Return ONLY a valid JSON object:
{{
  "table_objective": "Description of what this table achieves",
  "business_purpose": "The business value of this data",
  "final_sql": "The full SQL statement"
}}"""

    # 5. EXECUTE AGENT
    # NOTE: In deepagent.py, ensure you clear history or handle the 'tool' role 
    # if you are seeing the 'messages with role tool' error.
    return run_agent(
        session_id=session_id,
        user_input=instruction_prompt,
        use_history=False,
        persist_history=False,
    )
