from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import get_mcp_agent_response, get_mcp_stream_agent

app = FastAPI(title="MCP Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)