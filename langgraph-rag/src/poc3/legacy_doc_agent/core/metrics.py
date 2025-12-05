# core/metrics.py
import json
from datetime import datetime
from threading import Lock
from typing import Dict
from config import SAVE_METRICS_FILE


class Metrics:
    """
    Tracks global progress of documentation generation:
    folder-level, file-level, token usage, errors, agents spawned.
    No LLM calls – pure bookkeeping.
    """

    def __init__(self):
        self.lock = Lock()

        # counters
        self.folders_processed = 0
        self.files_processed = 0
        self.folder_agents_spawned = 0
        self.file_agents_spawned = 0

        # tokens and errors
        self.tokens_used = 0
        self.errors = 0
        self.error_messages = []

        # timing
        self.start_time = datetime.now().isoformat()
        self.end_time = None

        # execution status (optional feature)
        self.status = "running"  # running | completed | failed

    # --- safe increments ---
    def incr(self, field: str, n: int = 1):
        with self.lock:
            setattr(self, field, getattr(self, field) + n)

    # --- folder/file tracking ---
    def record_folder(self, n: int = 1):
        with self.lock:
            self.folders_processed += n

    def record_file(self, n: int = 1):
        with self.lock:
            self.files_processed += n

    def record_folder_agent(self, n: int = 1):
        with self.lock:
            self.folder_agents_spawned += n

    def record_file_agent(self, n: int = 1):
        with self.lock:
            self.file_agents_spawned += n

    # --- tokens tracking ---
    def update_tokens(self, n_tokens: int):
        """Increment token count without calling LLM"""
        with self.lock:
            self.tokens_used += max(0, int(n_tokens))

    # --- errors ---
    def record_error(self, msg: str = None):
        with self.lock:
            self.errors += 1
            if msg:
                self.error_messages.append(msg)
                self.status = "failed"

    # --- session finish ---
    def finish(self):
        with self.lock:
            self.end_time = datetime.now().isoformat()
            if self.errors == 0:
                self.status = "completed"

    def to_dict(self) -> Dict:
        with self.lock:
            return {
                "status": self.status,
                "folders_processed": self.folders_processed,
                "files_processed": self.files_processed,
                "folder_agents_spawned": self.folder_agents_spawned,
                "file_agents_spawned": self.file_agents_spawned,
                "tokens_used": self.tokens_used,
                "errors": self.errors,
                "error_messages": list(self.error_messages),
                "start_time": self.start_time,
                "end_time": self.end_time,
            }

    def save(self, path: str = SAVE_METRICS_FILE):
        with self.lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
