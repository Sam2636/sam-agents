# workers/file_agent.py
from pathlib import Path
import json
from utils.logger import get_logger
from core.tokenizer import count_tokens

logger = get_logger("FileAgent")

class FileAgent:
    def __init__(self, agent, metrics, system_prompt, doc_generator):
        self.agent = agent
        self.metrics = metrics
        self.system_prompt = system_prompt or "Generate documentation for this file."
        self.doc_generator = doc_generator

    def run(self, workspace_root: str, file_path: str):
        try:
            from core.metrics import Metrics
            self.metrics.record_file_agent(1)

            rel_path = Path(file_path).relative_to(Path(workspace_root))
            code = Path(file_path).read_text(encoding="utf-8", errors="ignore")

            instruction = f"""
            {self.system_prompt}
            Task: generate markdown documentation for the file below.
            Workspace root: {workspace_root}
            File relative path: {rel_path}
            File content:
            ```file
            {code}
            """

                        # Invoke deep agent
            result = self.agent.invoke({"messages":[{"role":"user","content": instruction}]})
            out = result.get("output") if isinstance(result, dict) else result
            md = out.strip() if isinstance(out, str) else json.dumps(out)

            saved = self.doc_generator.save_markdown(workspace_root, str(rel_path), md)
            self.metrics.record_file(1)
            self.metrics.update_tokens(len(instruction.split()) + len(md.split()))
            return {"ok": True, "path": saved}

        except Exception as e:
            logger.exception("FileAgent failed for %s: %s", file_path, e)
            self.metrics.record_error()
            return {"ok": False, "error": str(e)}
