# main.py
import os
import uuid
import zipfile
import shutil
import threading
import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.sqlite_store import SQLiteStore
# --- Persistent memory store ---
store = InMemoryStore()

# --- CompositeBackend: scratch workspace + persistent memory ---
def backend(rt):
    return CompositeBackend(
        default=StateBackend(rt),                  # ephemeral scratch workspace
        routes={"/memories/": StoreBackend(rt)}    # persistent memory for docs & TODOs
    )


from core.metrics import Metrics
from core.agent_manager import AgentManager
from workers.doc_generator import DocGenerator
from utils.logger import get_logger
from config import OPENAI_MODEL, MAIN_AGENT_PROMPT, OPENAI_API_KEY
from utils.open_utils import call_openai_with_retry

FILE_AGENT_PROMPT = MAIN_AGENT_PROMPT
FOLDER_AGENT_PROMPT = MAIN_AGENT_PROMPT

logger = get_logger("main")

app = FastAPI()

# allow your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_ROOT = Path("workspaces")
WORKSPACE_ROOT.mkdir(exist_ok=True)

# Global state
manager_thread = None
manager_lock = threading.Lock()
stop_event = threading.Event()
metrics = Metrics()
ws_connections = set()
ws_lock = threading.Lock()
llm = None
main_loop = None

# --- WebSocket broadcasting ---
async def broadcast_json(msg: dict):
    with ws_lock:
        conns = list(ws_connections)
    to_remove = []
    for ws in conns:
        try:
            await ws.send_text(json.dumps(msg))
        except Exception:
            to_remove.append(ws)
    if to_remove:
        with ws_lock:
            for ws in to_remove:
                ws_connections.discard(ws)

def progress_callback_sync(payload: dict):
    try:
        if main_loop:
            asyncio.run_coroutine_threadsafe(broadcast_json(payload), main_loop)
        else:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(asyncio.create_task, broadcast_json(payload))
    except Exception as e:
        logger.exception("Failed to schedule progress broadcast: %s", e)

# --- Startup ---
@app.on_event("startup")
async def startup_event():
    global llm, main_loop
    from deepagents import create_deep_agent

    # Ensure API key
    if not os.environ.get("OPENAI_API_KEY") and OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    folder_system_prompt = FOLDER_AGENT_PROMPT or """
    You are a legacy code repository analyzer.
    List all code files recursively from the given folder.
    """

    file_system_prompt = FILE_AGENT_PROMPT or """
    You are a legacy engineering documentation generator.
    Summarize code files in markdown.
    """

    # Create main deep agent
    llm = create_deep_agent(model=OPENAI_MODEL, system_prompt=file_system_prompt ,backend=backend,
    store=store)
    logger.info("DeepAgent initialized: %s", OPENAI_MODEL)

    try:
        main_loop = asyncio.get_running_loop()
    except RuntimeError:
        main_loop = None

# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    with ws_lock:
        ws_connections.add(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        with ws_lock:
            ws_connections.discard(ws)

# --- Upload ZIP ---
@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        return JSONResponse({"error": "Only zip files allowed"}, status_code=400)

    session_id = str(uuid.uuid4())
    session_folder = WORKSPACE_ROOT / session_id

    if session_folder.exists():
        shutil.rmtree(session_folder)  # clear if by any chance exists

    session_folder.mkdir(parents=True, exist_ok=False)
    zip_path = session_folder / file.filename

    try:
        # Save zip
        content = await file.read()
        zip_path.write_bytes(content)

        # Extract safely
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                member_path = session_folder / member
                abs_path = member_path.resolve()
                if not str(abs_path).startswith(str(session_folder.resolve())):
                    raise Exception(f"Unsafe file path: {member}")
            zip_ref.extractall(session_folder)

        zip_path.unlink()
    except Exception as e:
        shutil.rmtree(session_folder, ignore_errors=True)
        return JSONResponse({"error": str(e)}, status_code=500)

    return {"status": "uploaded", "session_id": session_id, "folder": str(session_folder)}

# --- Start processing ---
@app.post("/start")
async def start_processing(payload: dict):
    global manager_thread, stop_event, metrics
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    folder = WORKSPACE_ROOT / session_id
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=400, detail="Session folder not found. Upload ZIP first.")

    with manager_lock:
        if manager_thread and manager_thread.is_alive():
            return JSONResponse({"status": "running"}, status_code=200)
        if llm is None:
            raise HTTPException(status_code=503, detail="LLM not initialized yet")

        stop_event = threading.Event()
        metrics = Metrics()
        doc_generator = DocGenerator()

        # Session-specific store
        session_store = SQLiteStore(db_path=f"memory/{session_id}.db", namespace=session_id)

        logger.info("Starting AgentManager %s", folder)
        def target():
            try:
                am = AgentManager(
                    llm=llm,
                    metrics=metrics,
                    stop_event=stop_event,
                    progress_callback=progress_callback_sync,
                    doc_generator=doc_generator,
                    workspace_root=str(folder),
                    store=session_store
                )
                am.run()
            except Exception as e:
                logger.exception("AgentManager crashed: %s", e)
                if main_loop:
                    asyncio.run_coroutine_threadsafe(
                        broadcast_json({"event":"error","error":str(e)}),
                        main_loop
                    )

        manager_thread = threading.Thread(target=target, daemon=True)
        manager_thread.start()

    return {"status": "started", "folder": str(folder)}

# --- Stop processing ---
@app.post("/stop")
async def stop_processing():
    global stop_event
    stop_event.set()
    return {"status": "stop_requested"}

# --- Metrics ---
@app.get("/metrics")
async def get_metrics():
    return metrics.to_dict()

# --- Health endpoints ---
@app.get("/")
async def root():
    return {"status":"ok"}

@app.get("/ping")
async def ping():
    return {"status":"ok"}

from fastapi.responses import PlainTextResponse

# --- Fetch generated Markdown for a session ---
@app.get("/markdown/{session_id}")
async def get_markdown(session_id: str):
    """
    Returns combined Markdown content for a given session.
    Reads all .md files under the session folder recursively and concatenates them.
    """
    session_folder = WORKSPACE_ROOT / session_id
    if not session_folder.exists() or not session_folder.is_dir():
        raise HTTPException(status_code=404, detail="Session folder not found")

    md_contents = []
    for root, dirs, files in os.walk(session_folder):
        for fname in files:
            if fname.endswith(".md"):
                file_path = Path(root) / fname
                try:
                    md_contents.append(file_path.read_text(encoding="utf-8"))
                except Exception as e:
                    logger.warning("Failed to read %s: %s", file_path, e)

    if not md_contents:
        return PlainTextResponse("No Markdown generated yet.", status_code=200)

    # Combine all markdown files into a single response
    combined_md = "\n\n".join(md_contents)
    return PlainTextResponse(combined_md, status_code=200)
