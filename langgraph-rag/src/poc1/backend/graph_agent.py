from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.graph import StateGraph, MessagesState, START, END
import uvicorn
import asyncio

# -----------------------------
# Define request model
# -----------------------------
class QueryRequest(BaseModel):
    query: str

# -----------------------------
# Define mock LangGraph node
# -----------------------------
async def mock_llm(state: MessagesState):
    """Simulated LLM node that echoes a response"""
    user_message = state["messages"][-1]["content"]
    return {"messages": [{"role": "ai", "content": f"Echo from LangGraph: {user_message}"}]}

# -----------------------------
# Build the LangGraph
# -----------------------------
graph = StateGraph(MessagesState)
graph.add_node("mock_llm", mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

# -----------------------------
# FastAPI setup
# -----------------------------
app = FastAPI(title="LangGraph FastAPI Example")

@app.post("/run-graph")
async def run_graph(req: QueryRequest):
    """Execute LangGraph graph synchronously (but still async) and return final response."""
    input_state = {"messages": [{"role": "user", "content": req.query}]}
    try:
        result = await graph.ainvoke(input_state)
        # Extract the last AI message
        ai_content = result["messages"][-1]["content"]
        return {"response": ai_content}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
