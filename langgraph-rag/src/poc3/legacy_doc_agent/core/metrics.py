# core/metrics.py
import json
from datetime import datetime
from threading import Lock
from typing import Dict
from config import SAVE_METRICS_FILE

class Metrics:
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

    # safe increments
    def incr(self, field: str, n: int = 1):
        with self.lock:
            if hasattr(self, field):
                setattr(self, field, getattr(self, field) + n)
            else:
                raise AttributeError(f"Metrics has no field '{field}'")

    # convenience methods used by agents
    def record_folder(self, n: int = 1):
        with self.lock:
            self.folders_processed += int(n)

    def record_file(self, n: int = 1):
        with self.lock:
            self.files_processed += int(n)

    def record_folder_agent(self, n: int = 1):
        with self.lock:
            self.folder_agents_spawned += int(n)

    def record_file_agent(self, n: int = 1):
        with self.lock:
            self.file_agents_spawned += int(n)

    def update_tokens(self, n_tokens: int):
        with self.lock:
            self.tokens_used += max(0, int(n_tokens))

    def record_error(self, msg: str = None):
        with self.lock:
            self.errors += 1
            if msg:
                self.error_messages.append(msg)

    def finish(self):
        with self.lock:
            self.end_time = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        with self.lock:
            return {
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
