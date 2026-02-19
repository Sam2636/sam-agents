import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from app.api.chat import _tables_from_session_csv, fetch_table_schema
from app.memory.session_context import save_context
import asyncio
import logging
from app.config import SESSION_UPLOADS_DIR
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import pandas as pd
from pandas.errors import ParserError
router = APIRouter()


def _session_dir(session_id: str) -> Path:
    root = Path(SESSION_UPLOADS_DIR)
    root.mkdir(parents=True, exist_ok=True)
    session_path = root / session_id
    session_path.mkdir(parents=True, exist_ok=True)
    return session_path


def _read_csv_with_fallback(file_path: Path):
    try:
        return pd.read_csv(file_path)
    except ParserError as err:
        logger.warning("CSV parse failed with C engine for %s: %s", file_path.name, err)
        return pd.read_csv(file_path, engine="python", on_bad_lines="skip")

@router.post("/upload")
async def upload_csv_files(files: list[UploadFile] = File(...)):

    session_id = str(uuid4())
    session_path = _session_dir(session_id)

    saved_files = []

    for file in files:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files allowed.")

        destination = session_path / file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(file.filename)

    # 🔥 BUILD GRAPH CONTEXT
    tables = _tables_from_session_csv(session_id)

    graph_context = {}

    for table in tables:
        try:
            schema_data = await fetch_table_schema(table)
            logger.info(f"Fetching schema for table: {table}")
            logger.info(f"Schema returned: {schema_data}")

            if schema_data:
                graph_context[table] = schema_data
        except Exception:
            continue
    
    # ----------------------------------------
    # BUILD BUSINESS SPEC FROM CSV
    # ----------------------------------------

    business_spec = {}
    warnings = []

    session_path = Path(SESSION_UPLOADS_DIR) / session_id
    csv_files = list(session_path.glob("*.csv"))
    required_columns = {
        "layer",
        "schema",
        "table_name",
        "table_type",
        "source_tables",
        "column_name",
        "transformation_logic",
    }

    for file_path in csv_files:
        try:
            df = _read_csv_with_fallback(file_path)
        except Exception as err:
            msg = f"Skipped '{file_path.name}' due to parse error: {err}"
            logger.warning(msg)
            warnings.append(msg)
            continue

        df.columns = [str(col).strip().lower() for col in df.columns]
        missing = sorted(required_columns - set(df.columns))
        if missing:
            msg = f"Skipped '{file_path.name}' missing required columns: {', '.join(missing)}"
            logger.warning(msg)
            warnings.append(msg)
            continue

        grouped = df.groupby(["layer", "schema", "table_name"])

        for (layer, schema, table), group_df in grouped:
            full_name = f"{layer}.{schema}.{table}"

            business_spec[full_name] = {
                "type": group_df["table_type"].iloc[0],
                "source": group_df["source_tables"].iloc[0],
                "columns": {}
            }

            for _, row in group_df.iterrows():
                business_spec[full_name]["columns"][
                    row["column_name"]
                ] = row["transformation_logic"]


    save_context(session_id, {
    "source_tables": list(tables),
    "graph_context": graph_context,
    "business_spec": business_spec
    })


    return {
        "status": "uploaded",
        "session_id": session_id,
        "workspace": str(session_path),
        "files": saved_files,
        "tables_detected": list(tables),
        "warnings": warnings,
    }



@router.get("/session/{session_id}")
def get_session_files(session_id: str):
    session_path = _session_dir(session_id)
    files = [str(p) for p in session_path.glob("*.csv") if p.is_file()]
    return {
        "session_id": session_id,
        "workspace": str(session_path),
        "files": files,
    }
