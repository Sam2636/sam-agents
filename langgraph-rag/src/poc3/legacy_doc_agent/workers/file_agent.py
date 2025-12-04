# workers/file_agent.py
from pathlib import Path
import json
from utils.logger import get_logger
from core.tokenizer import count_tokens

logger = get_logger("FileAgent")

import time

def invoke_with_retry(agent, payload, retries=6):
    for attempt in range(retries):
        try:
            return agent.invoke(payload)

        except Exception as e:
            wait = min(2 ** attempt, 30)   # 1,2,4,8,16,30 sec
            print(f"[RateLimit] retry {attempt+1}/{retries} → waiting {wait}s")
            time.sleep(wait)

    raise Exception("Max retries exceeded")


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
                # Call LLM
            payload = {"messages": [{"role": "user", "content": instruction}]}
            result = invoke_with_retry(self.agent, payload)


            # Extract output properly
            if isinstance(result, str):
                md = result.strip()
            elif isinstance(result, dict):
                md = (result.get("output") or result.get("content") or str(result))
            elif hasattr(result, "content"):  # AIMessage
                md = str(result.content).strip()
            else:
                md = str(result)
            # Save docs
            saved = self.doc_generator.save_markdown(workspace_root, str(rel_path), md)

            self.metrics.record_file(1)
            self.metrics.update_tokens(len(instruction.split()) + len(md.split()))

            return {"ok": True, "path": saved}

        except Exception as e:
            logger.exception("FileAgent failed for %s: %s", file_path, e)
            self.metrics.record_error()
            return {"ok": False, "error": str(e)}
