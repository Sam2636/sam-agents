# utils/fs_utils.py
import os
from pathlib import Path
from typing import Generator
from config import CODE_EXTENSIONS

def list_code_files(folder: str) -> Generator[str, None, None]:
    folder = Path(folder)
    for root, _, files in os.walk(folder):
        for file in files:
            p = Path(root) / file
            if p.suffix.lower() in CODE_EXTENSIONS:
                yield str(p)
