# core/agent_manager.py
from workers.folder_agent import FolderAgent
from utils.logger import get_logger
logger = get_logger("agent_manager")

class AgentManager:
    def __init__(self, llm, metrics, stop_event, progress_callback, doc_generator, workspace_root, store):
        self.llm = llm
        self.metrics = metrics
        self.stop_event = stop_event
        self.progress_callback = progress_callback
        self.doc_generator = doc_generator
        self.workspace_root = workspace_root
        self.store = store

    def run(self):
        """Manage the workflow for a session: folder → files"""
        try:
            folder_agent = FolderAgent(
                agent=self.llm,
                metrics=self.metrics,
                system_prompt="Generate markdown docs for files",
                doc_generator=self.doc_generator,
                store=self.store
            )
            logger.info("Starting FolderAgent for workspace: %s", self.workspace_root)
            results = folder_agent.run(self.workspace_root, self.workspace_root)
            
            # Optionally, broadcast progress or log
            self.progress_callback({"event": "completed", "results": results})

        except Exception as e:
            if self.progress_callback:
                self.progress_callback({"event": "error", "error": str(e)})
            raise e
