# workers/folder_agent.py (only run() method replaced)
import os
from pathlib import Path
from workers.file_agent import FileAgent
from utils.logger import get_logger

logger = get_logger("FolderAgent")


class FolderAgent:
    def __init__(self, agent, metrics, system_prompt, doc_generator, store, progress_callback=None):
        """
        Args:
            agent: LLM / deep agent
            metrics: Metrics object
            system_prompt: Documentation prompt
            doc_generator: Markdown generator
            store: Session memory store (SQLite/in-memory)
            progress_callback: WebSocket push callback for metrics & status
        """
        self.agent = agent
        self.metrics = metrics
        self.system_prompt = system_prompt
        self.doc_generator = doc_generator
        self.store = store
        self.progress_callback = progress_callback  # NEW

    def run(self, workspace_root: str, folder_path: str):
        try:
            self.metrics.record_folder_agent(1)

            folder = Path(folder_path)
            logger.info(f"📁 Starting folder processing: {folder_path}")
            if not folder.exists() or not folder.is_dir():
                raise Exception(f"Folder not found: {folder_path}")

            file_agent = FileAgent(
                agent=self.agent,
                metrics=self.metrics,
                system_prompt=self.system_prompt,
                doc_generator=self.doc_generator,
                store=self.store,
                progress_callback=self.progress_callback,
            )

            # --- Pre-walk to compute totals ---
            total_files = 0
            total_folders = 0
            first = True
            for root, dirs, files in os.walk(folder_path):
                if first:
                    first = False
                    continue
                total_folders += 1
                total_files += len(files)

            logger.info(f"📊 Counted totals → folders={total_folders}, files={total_files}")

            combined_total = total_folders + total_files if (total_folders + total_files) > 0 else 1

            results = []
            processed_files = 0
            processed_folders = 0
            combined_progress = 0

            # --- Main processing ---
            first = True
            for root, dirs, files in os.walk(folder_path):
                if first:
                    first = False
                    continue

                # Folder entered
                processed_folders += 1
                combined_progress += 1

                if self.progress_callback:
                    self.progress_callback({
                        "event": "folder_enter",
                        "folder": str(root),
                        "processed_folders": processed_folders,
                        "total_folders": total_folders,
                        "combined_progress": combined_progress,
                        "combined_total": combined_total,
                        "metrics": self.metrics.to_dict()
                    })

                # Process each file
                for fname in files:
                    file_path = os.path.join(root, fname)
                    logger.info(f"📄 Processing file: {file_path}")

                    res = file_agent.run(workspace_root, str(file_path))
                    results.append(res)

                    processed_files += 1
                    combined_progress += 1

                    if self.progress_callback:
                        pct = round((combined_progress / combined_total) * 100, 2)
                        self.progress_callback({
                            "event": "progress",
                            "current_file": processed_files,
                            "total_files": total_files,
                            "processed_folders": processed_folders,
                            "total_folders": total_folders,
                            "combined_progress": combined_progress,
                            "combined_total": combined_total,
                            "pct": pct,
                            "metrics": self.metrics.to_dict()
                        })

                # Record folder metrics (only once per folder)
                self.metrics.record_folder(1)

            # --- Final broadcast after entire folder tree is done ---
            if self.progress_callback:
                self.progress_callback({
                    "event": "folder_complete",
                    "folder": str(folder_path),
                    "files_processed": processed_files,
                    "folders_processed": processed_folders,
                    "metrics": self.metrics.to_dict()
                })

            return {
                "ok": True,
                "folder": str(folder_path),
                "files_processed": processed_files,
                "folders_processed": processed_folders,
                "results": results,
            }

        except Exception as e:
            logger.exception("FolderAgent failed: %s", e)
            self.metrics.record_error(str(e))

            if self.progress_callback:
                self.progress_callback({
                    "event": "error",
                    "folder": str(folder_path),
                    "error": str(e),
                    "metrics": self.metrics.to_dict()
                })

            return {"ok": False, "folder": str(folder_path), "error": str(e)}
