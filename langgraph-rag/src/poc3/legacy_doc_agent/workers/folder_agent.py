from time import sleep
from pathlib import Path
from workers.file_agent import FileAgent

class FolderAgent:
    def __init__(self, agent, metrics, system_prompt, doc_generator, workspace_root, progress_callback, stop_event):
        self.agent = agent
        self.metrics = metrics
        self.system_prompt = system_prompt
        self.doc_generator = doc_generator
        self.workspace_root = workspace_root
        self.progress_callback = progress_callback
        self.stop_event = stop_event

    def run(self):
        files = [str(f) for f in Path(self.workspace_root).rglob("*") if f.is_file()]
        total = len(files)
        if total == 0:
            return

        processed = 0

        for fp in files:
            if self.stop_event.is_set():
                break

            fa = FileAgent(self.agent, self.metrics, self.system_prompt, self.doc_generator)
            fa.run(self.workspace_root, fp)

            # small delay to reduce rate limit hits
            sleep(0.003)  # 3 ms

            processed += 1
            pct = (processed / total) * 100
            self.progress_callback({
                "event": "progress",
                "processed": processed,
                "total": total,
                "pct": pct,
                "last_file": fp,
                "metrics": self.metrics.to_dict()
            })
