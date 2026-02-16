import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import SESSION_UPLOADS_DIR

router = APIRouter()


def _session_dir(session_id: str) -> Path:
    root = Path(SESSION_UPLOADS_DIR)
    root.mkdir(parents=True, exist_ok=True)
    session_path = root / session_id
    session_path.mkdir(parents=True, exist_ok=True)
    return session_path


@router.post("/upload")
async def upload_csv_files(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    session_id = uuid4().hex
    session_path = _session_dir(session_id)
    saved_files: list[str] = []

    for upload in files:
        filename = Path(upload.filename or "").name
        if not filename:
            continue
        if not filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail=f"Only CSV files are supported: {filename}")

        target = session_path / filename
        with target.open("wb") as f:
            shutil.copyfileobj(upload.file, f)
        saved_files.append(str(target))

    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid CSV files were uploaded")

    return {
        "status": "uploaded",
        "session_id": session_id,
        "workspace": str(session_path),
        "files": saved_files,
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
