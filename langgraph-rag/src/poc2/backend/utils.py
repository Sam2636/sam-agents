# utils.py
import os
import zipfile
from pathlib import Path

ALLOWED_EXT = {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"}

def ensure_dirs(paths):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)

def safe_extract_zip(zip_path: Path, dest_dir: Path):
    # Prevent zip slip attacks
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.namelist():
            member_path = Path(dest_dir) / member
            if not str(member_path.resolve()).startswith(str(Path(dest_dir).resolve())):
                raise Exception("Illegal zip member")
        zf.extractall(dest_dir)

def list_source_files(root: Path):
    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in ALLOWED_EXT:
            files.append(p)
    return files

def save_md(path: str, content: str):
    p = Path(path)
    p.write_text(content, encoding="utf8")
