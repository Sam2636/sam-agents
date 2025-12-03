# app.py
import os
import zipfile
import uuid
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from worker import process_file_worker
from utils import safe_extract_zip, list_source_files, ensure_dirs

WORKSPACE_ROOT = Path("workspaces")
OUTPUT_ROOT = Path("docs-output")
MAX_FILES = 200
MAX_WORKSPACE_SIZE = 200 * 1024 * 1024  # 200 MB

app = FastAPI()
ensure_dirs([WORKSPACE_ROOT, OUTPUT_ROOT])

@app.post("/upload")
async def upload_and_process(zip_file: UploadFile = File(...)):
    # create session workspace
    session_id = uuid.uuid4().hex[:12]
    workspace = WORKSPACE_ROOT / session_id
    workspace.mkdir(parents=True, exist_ok=True)

    # save zip
    zip_bytes = await zip_file.read()
    zip_path = workspace / "upload.zip"
    zip_path.write_bytes(zip_bytes)

    # extract safely
    try:
        safe_extract_zip(zip_path, workspace)
    except Exception as e:
        shutil.rmtree(workspace, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"Invalid zip or extraction error: {e}")

    # optional workspace size guard
    total_size = sum(p.stat().st_size for p in workspace.rglob("*") if p.is_file())
    if total_size > MAX_WORKSPACE_SIZE:
        shutil.rmtree(workspace, ignore_errors=True)
        raise HTTPException(status_code=400, detail="Workspace too large")

    # find source files
    source_files = list_source_files(workspace)
    if not source_files:
        shutil.rmtree(workspace, ignore_errors=True)
        return JSONResponse({"error": "No source files (.c/.cpp/.h/.hpp) found"}, status_code=400)

    if len(source_files) > MAX_FILES:
        shutil.rmtree(workspace, ignore_errors=True)
        return JSONResponse({"error": f"Too many files (>{MAX_FILES})"}, status_code=400)

    # Process files in parallel with ThreadPoolExecutor (subagents)
    results = {}
    futures = []
    with ThreadPoolExecutor(max_workers=min(8, len(source_files))) as ex:
        for path in source_files:
            # spawn subagent (worker) for this file
            futures.append(ex.submit(process_file_worker, str(path), str(workspace)))

        for fut in as_completed(futures):
            try:
                r = fut.result()
                results[r["file_name"]] = r
            except Exception as e:
                # log and continue
                results[f"error_{len(results)}"] = {"error": str(e)}

    # create an archive of generated docs
    output_files = [r["md_path"] for r in results.values() if "md_path" in r]
    archive_path = OUTPUT_ROOT / f"{session_id}_docs.zip"
    with zipfile.ZipFile(archive_path, "w") as zf:
        for p in output_files:
            ppath = Path(p)
            if ppath.exists():
                zf.write(ppath, arcname=ppath.name)

    return {"session_id": session_id, "workspace": str(workspace), "results": results, "docs_archive": str(archive_path)}
