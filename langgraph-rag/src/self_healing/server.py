import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="LangChain MCP Chat API")

# Initialize global resources
client = None
agent = None

@app.on_event("startup")
async def startup_event():
    global client, agent
    client = MultiServerMCPClient({
        "mysql_server": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    })
    tools = await client.get_tools()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    SYSTEM_PROMPT = """
    You are a database assistant that interacts with a MySQL MCP server.
    - Use `test_connection` to check DB connectivity.
    - Use `list_tables` to inspect the schema.
    - Use `run_query` for SQL operations.
    Always respond in markdown.
    """

    agent = create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT)

@app.post("/chat")
async def chat(request: Request):
    """Handle user chat requests."""
    data = await request.json()
    user_message = data.get("message", "")
    if not user_message:
        return JSONResponse({"error": "Message cannot be empty"}, status_code=400)

    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": user_message}]
    })
    return {"response": str(response)}
