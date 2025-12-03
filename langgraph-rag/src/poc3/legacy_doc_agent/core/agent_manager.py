# core/agent_manager.py
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from workers.folder_agent import FolderAgent

class AgentManager:
    def __init__(self, llm, metrics, stop_event, progress_callback, doc_generator, workspace_root):
        self.llm = llm
        self.metrics = metrics
        self.stop_event = stop_event
        self.progress_callback = progress_callback
        self.doc_generator = doc_generator
        self.workspace_root = workspace_root

    def run(self):
        # Create FolderAgent and run parallel file processing
        folder_agent = FolderAgent(
            agent=self.llm,
            metrics=self.metrics,
            system_prompt=None,  # set if needed
            doc_generator=self.doc_generator,
            workspace_root=self.workspace_root,
            progress_callback=self.progress_callback,
            stop_event=self.stop_event
        )
        folder_agent.run()
