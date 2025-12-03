# workers/doc_generator.py
from pathlib import Path
import json
from utils.logger import get_logger
from config import DOC_OUTPUT_DIR

logger = get_logger("DocGenerator")

class DocGenerator:
    def __init__(self, output_dir: str = DOC_OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_markdown(self, workspace_root: str, rel_path: str, markdown: str):
        """
        Save markdown inside workspace/docs preserving relative path.
        rel_path should be relative to workspace_root, e.g. 'src/module/file.cs'
        """
        try:
            docs_root = Path(workspace_root) / "docs"
            out_path = docs_root / Path(rel_path).with_suffix(".md")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(markdown, encoding="utf-8")
            logger.info("Wrote doc %s", out_path)
            return str(out_path)
        except Exception as e:
            logger.exception("Failed to write markdown for %s: %s", rel_path, e)
            raise

    def save_json(self, workspace_root: str, rel_path: str, obj):
        try:
            docs_root = Path(workspace_root) / "docs"
            out_path = docs_root / Path(rel_path).with_suffix(".json")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
            logger.info("Wrote json doc %s", out_path)
            return str(out_path)
        except Exception as e:
            logger.exception("Failed to write json for %s: %s", rel_path, e)
            raise
