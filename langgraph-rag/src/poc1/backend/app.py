from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import get_mcp_agent_response, get_mcp_stream_agent
from langgraph.graph import StateGraph, MessagesState, START, END
import asyncio


class QueryRequest(BaseModel):
    query: str

# ----------------------------
# Define your graph nodes
# ----------------------------
from langchain_core.messages import AIMessage

async def mock_llm(state: MessagesState):
    last_msg = state["messages"][-1]
    user_text = last_msg.content
    return {"messages": [AIMessage(content=f"Hello! You said: {user_text}")]}

# ----------------------------
# Build and compile the state graph
# ----------------------------
graph = StateGraph(MessagesState)
graph.add_node("mock_llm", mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()


app = FastAPI(title="MCP Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "MCP Agent API running 🚀"}

@app.post("/query")
async def query_agent(req: QueryRequest):
    response = await get_mcp_agent_response(req.query)
    return {"response": response}

@app.post("/stream-query")
async def stream_query(req: QueryRequest):
    """Streams tokens in real-time"""
    return StreamingResponse(
        get_mcp_stream_agent(req.query),
        media_type="text/event-stream"
    )

@app.post("/stream-query-llm")
async def stream_query_llm(req: QueryRequest):
    """Stream LangGraph LLM node output as Server-Sent Events"""

    async def generate():
        # Run your async graph
        result = await graph.ainvoke({
            "messages": [{"role": "user", "content": req.query}]
        })

        # Extract response
        ai_msg = result["messages"][-1]["content"]

        # Stream token by token
        for token in ai_msg.split():
            yield f"data: {token}\n\n"

        # Send completion signal
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/run-graph")
async def run_graph(req: QueryRequest):
    """Execute the LangGraph pipeline"""
    try:
        input_state = {"messages": [{"role": "user", "content": req.query}]}
        result = await graph.ainvoke(input_state)
        ai_response = result["messages"][-1].content  # ✅ Access property, not dict
        return {"response": ai_response}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)