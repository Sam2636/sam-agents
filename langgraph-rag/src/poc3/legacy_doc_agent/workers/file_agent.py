# workers/file_agent.py
from pathlib import Path
import time
from utils.logger import get_logger
from core.tokenizer import count_tokens
from langchain.messages import AIMessage
logger = get_logger("FileAgent")


def invoke_with_retry(agent, payload, retries=6):
    """Retry LLM call on failure with exponential backoff."""
    for attempt in range(retries):
        try:
            return agent.invoke(payload)
        except Exception as e:
            wait = min(3 ** attempt, 30)
            logger.warning(f"[RateLimit] retry {attempt+1}/{retries} → waiting {wait}s")
            time.sleep(wait)
    raise Exception("Max retries exceeded")


class FileAgent:
    def __init__(self, agent, metrics, system_prompt, doc_generator, store=None, progress_callback=None):
        self.agent = agent
        self.metrics = metrics
        self.system_prompt = system_prompt or "Generate documentation for this file."
        self.doc_generator = doc_generator
        self.store = store
        self.progress_callback = progress_callback        # <── callback for WS events

    def run(self, workspace_root: str, file_path: str):
        start_t = time.time()

        try:
            import os
            rel_path = Path(os.path.relpath(file_path, workspace_root))

            code = Path(file_path).read_text(encoding="utf-8", errors="ignore")
            #logger.info("Reading file:########## %s", file_path)
            #logger.info("Relative path: #########%s", rel_path)
            #logger.info("File content (first 100 chars)#######: %s", code[:100])

            # ---- Metrics: file agent activation ---- 
            self.metrics.record_file_agent(1)

            # ---- Build prompt ----
            instruction = (
                f"{self.system_prompt}\n"
                f"Task: generate markdown documentation for the file below.\n"
                f"Workspace root: {workspace_root}\n"
                f"File relative path: {rel_path}\n\n"

                #  New formatting enforcement
                f"### OUTPUT FORMAT RULES (STRICT)\n"
                f"- Output must be **pure Markdown only**.\n"
                f"- Do **NOT** include explanations, comments, or conversational responses.\n"
                f"- Do **NOT** wrap the Markdown in backticks.\n"
                f"- Do **NOT** include the source code of the file, only documentation.\n"
                f"- Must follow this structure:\n"
                f"  # <ClassName> Class\n"
                f"\n"
                f"  **Namespace:** `<namespace>`\n"
                f"\n"
                f"  ## Description\n"
                f"  <1–3 sentences about what the class does>\n"
                f"\n"
                f"  ## Methods\n"
                f"  ### <MethodName>(parameters)\n"
                f"  - **Summary:** what it does\n"
                f"  - **Parameters:** bullet list name + type + meaning\n"
                f"  - **Returns:** return type + description\n"
                f"\n"
                f"  ## Example\n"
                f"  Provide C# usage snippet.\n\n"

                # Keep your original file content part untouched
                f"```file\n{code}\n```"
            )


            # ---- Add session context if available ----
            if self.store:
                previous_ctx = self.store.get("last_file")
                if previous_ctx: 
                    instruction = previous_ctx + "\n\n" + instruction

            payload = {"messages": [{"role": "user", "content": instruction}]}

            # ---- LLM call ----
            result = invoke_with_retry(self.agent, payload)
            logger.info(f"LLM response received for {rel_path}")
            #logger.info(f"LLM raw response: {result}")
            logger.info(f"workspace completed for {workspace_root}")
            # ---- Extract markdown from LLM ----
            # Extract only AI message content dynamically
            md = ""
            logger.info(f"Result is AIMessage for {result}")
            # Case 1: Result is a single AIMessage

            md = ""

            # If result is a dict with 'messages'
            if isinstance(result, dict) and "messages" in result:
                for msg in result["messages"]:
                    if isinstance(msg, AIMessage) and msg.content.strip():
                        md = msg.content.strip()
                        break

            # Fallback if result is directly an AIMessage
            elif isinstance(result, AIMessage):
                md = result.content.strip()

            # If result is a list of messages
            elif isinstance(result, list):
                for msg in result:
                    if isinstance(msg, AIMessage) and msg.content.strip():
                        md = msg.content.strip()
                        break

            # Fallback string
            elif isinstance(result, str):
                md = result.strip()

            # Final fallback
            else:
                md = str(result).strip()

            logger.info(f"Extracted markdown for {rel_path}: {md[:100]}...")



            # ---- Save markdown output ----
            #logger.info(f"Generated documentation for ---<>><><{md}")
            saved = self.doc_generator.save_markdown(workspace_root, str(rel_path), md)
            #logger.info(f"Documentation saved for ---<>><><{rel_path} at {saved}")
            # ---- Tokens & metrics ----
            prompt_tokens = count_tokens(instruction)
            completion_tokens = count_tokens(md)
            used_tokens = prompt_tokens + completion_tokens
            self.metrics.update_tokens(used_tokens)
            self.metrics.record_file(1)

            # ---- Save last file to persistent store ----
            if self.store:
                self.store.set("last_file", f"Processed {rel_path}\n\n{md}")

            # ---- WebSocket broadcast ----
            if self.progress_callback:
                self.progress_callback({
                    "event": "metrics",
                    "file": str(rel_path),
                    "tokens": used_tokens,
                    "time_secs": round(time.time() - start_t, 2),
                    "metrics": self.metrics.to_dict()
                })

            return {"ok": True, "path": saved}

        except Exception as e:
            logger.exception("FileAgent failed for %s: %s", file_path, e)
            self.metrics.record_error(str(e))

            if self.progress_callback:
                self.progress_callback({
                    "event": "error",
                    "file": str(file_path),
                    "error": str(e),
                    "metrics": self.metrics.to_dict()
                })

            return {"ok": False, "file": str(file_path), "error": str(e)}
