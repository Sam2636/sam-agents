import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langsmith import traceable
import langsmith
from langsmith.wrappers import wrap_openai
from openai import OpenAI  # ✅ correct import

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "MCP-Agent-Demo"
api_key = os.getenv("OPENAI_API_KEY")
langsmith_key = os.getenv("LANGSMITH_API_KEY")  # ✅ Add this to your .env

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env")

if not langsmith_key:
    raise ValueError("❌ LANGSMITH_API_KEY not found in .env")

# -------------------------------
# Wrap OpenAI client for LangSmith tracing
# -------------------------------
openai_client = wrap_openai(OpenAI(api_key=api_key))

# -------------------------------
# Create MCP-connected LangChain agent
# -------------------------------
async def get_agent():
    client = MultiServerMCPClient({
        "mysql_server": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    })

    tools = await client.get_tools()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

    SYSTEM_PROMPT = """
    You are a database assistant that interacts with a MySQL MCP server.
    - Use `test_connection` to check DB connectivity.
    - Use `list_tables` to inspect the schema.
    - Use `run_query` for SQL operations.
    Always show SQL queries in ```sql blocks.
    """

    return create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT)

# -------------------------------
# Regular (non-streaming) response
# -------------------------------
async def get_mcp_agent_response(query: str):
    agent = await get_agent()
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": query}]
    })
    return response

# -------------------------------
# Streaming response
# -------------------------------
@traceable
async def get_mcp_stream_agent(query: str):
    client = MultiServerMCPClient({
        "mysql_server": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    })

    tools = await client.get_tools()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

    SYSTEM_PROMPT = """
    You are a database assistant that interacts with a MySQL MCP server.
    - Use `test_connection` to check database connectivity.
    - Use `list_tables` to inspect the schema.
    - Use `run_query` for SQL operations.
    Format your responses in **clear Markdown**, and wrap SQL queries inside ```sql code blocks.
    """

    agent = create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT)

    async for event in agent.astream_events({"messages": [{"role": "user", "content": query}]}):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"].content
            yield f"data: {chunk}\n\n"

    yield "data: [DONE]\n\n"
