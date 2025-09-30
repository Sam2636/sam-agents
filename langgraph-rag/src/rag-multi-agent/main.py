import os
from dotenv import load_dotenv

# ----------------------------
# Load environment variables
# ----------------------------
# The .env file is assumed to be outside the src folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(project_root, ".env"))

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env!")

# ----------------------------
# Import after loading .env
# ----------------------------
from langchain_openai import ChatOpenAI
from utils.vectorstore import build_vectorstore
from agents.retriever_agent import get_retriever_agent
from agents.summarizer_agent import get_summarizer_agent
from agents.qa_agent import get_qa_agent
from graph import build_graph

# ----------------------------
# Sample documents for RAG
# ----------------------------
docs = [
    "LangGraph is a framework for building stateful multi-agent systems.",
    "RAG stands for Retrieval Augmented Generation.",
    "It allows LLMs to fetch external knowledge when answering questions."
]

# ----------------------------
# Build vectorstore for retrieval
# ----------------------------
vectorstore = build_vectorstore(docs)

# ----------------------------
# Initialize LLM
# ----------------------------
llm = ChatOpenAI(api_key=api_key, model=model_name)

# ----------------------------
# Initialize Agents
# ----------------------------
retriever_agent = get_retriever_agent(vectorstore, llm)
summarizer_agent = get_summarizer_agent(llm)
qa_agent = get_qa_agent(llm)

# ----------------------------
# Build the multi-agent graph
# ----------------------------
graph = build_graph(retriever_agent, summarizer_agent, qa_agent)

# ----------------------------
# Define initial state
# ----------------------------
# In LangGraph 0.6.8, state schema must match the keys in StateGraph
state = {
    "context": "",
    "question": "What is RAG and how does LangGraph help?",
    "answer": ""
}

# ----------------------------
# Run the graph
# ----------------------------
# Note: run_sync() no longer exists in v0.6.8
# Use execute(state) instead for synchronous execution
app = graph.compile()

# Run synchronously
final_state = app.invoke(state)

# After building your graph but before compile
graph_image = app.get_graph().draw_mermaid()
print(graph_image)

# ----------------------------
# Print results
# ----------------------------
print("Question:", final_state["question"])
print("Answer:", final_state["answer"])

# ----------------------------
# Optional: Print intermediate state for debugging
# ----------------------------
print("\nFull state after execution:")
for key, value in final_state.items():
    print(f"{key}: {value}")
