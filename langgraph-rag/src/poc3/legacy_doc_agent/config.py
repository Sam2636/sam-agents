# config.py
from dotenv import load_dotenv
import os

load_dotenv()

# LLM / DeepAgent config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# output & metrics
DOC_OUTPUT_DIR = os.getenv("DOC_OUTPUT_DIR", "generated_docs")
SAVE_METRICS_FILE = os.getenv("SAVE_METRICS_FILE", "metrics.json")
WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "workspaces")

# operational
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "8"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "16000"))

# system prompts (you can edit to tune behavior)
MAIN_AGENT_PROMPT = os.getenv("MAIN_AGENT_PROMPT", """
You are the top-level repository documentation agent. Given a path on disk,
you must create a `docs/` directory inside that path and generate
Markdown documentation for the repository: README, module overviews,
API reference, and per-file documentation. Use subagents to process many files
and avoid returning raw code. Write docs to disk using the filesystem tools.
""".strip())

SUBAGENT_PROMPT = os.getenv("SUBAGENT_PROMPT", """
You are a file-level documentation subagent. Your job is to read a single source
file and produce a structured Markdown document describing public functions,
classes, examples, and a short summary. Return a short JSON status after writing.
""".strip())
