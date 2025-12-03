# worker.py
import os
import json
from pathlib import Path
from parser import parse_file_to_json
from llm_client import json_to_markdown
from utils import save_md

def process_file_worker(file_path: str, workspace_root: str):
    """
    Acts as a subagent for a single file.
    1. Run deterministic parser -> JSON
    2. Call LLM to convert JSON -> Markdown
    3. Save resulting Markdown to workspace/docs/
    Returns a dict with metadata.
    """
    p = Path(file_path)
    parsed = parse_file_to_json(str(p))

    # include some metadata
    parsed["source_file"] = p.name
    parsed["workspace"] = workspace_root

    # Call LLM (json -> Markdown)
    md_text = json_to_markdown(parsed)

    docs_dir = Path(workspace_root) / "generated_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    md_name = f"{p.stem}.md"
    md_path = docs_dir / md_name
    save_md(str(md_path), md_text)

    return {
        "file_name": p.name,
        "json": parsed,
        "md_path": str(md_path)
    }
