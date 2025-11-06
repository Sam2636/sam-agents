import os
import asyncio
import markdown
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env")

async def get_agent():
    """Creates and returns an MCP-connected LangChain agent"""
    client = MultiServerMCPClient({
        "mysql_server": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    })
    tools = await client.get_tools()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0,streaming=True)

    SYSTEM_PROMPT = """
    You are a database assistant that interacts with a MySQL MCP server.
    - Use `test_connection` to check DB connectivity.
    - Use `list_tables` to inspect the schema.
    - Use `run_query` for SQL operations.
    Always show SQL queries in ```sql blocks.
    """
    agent = create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT)
    return agent

import re


async def get_mcp_agent_response(query: str):
    """Handles normal (non-streaming) responses"""
    agent = await get_agent()
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": query}]
    })
    return response

async def get_mcp_stream_agent(query: str):
    """Stream MCP agent responses with clean Markdown formatting"""
    # Connect to MCP MySQL server
    client = MultiServerMCPClient({
        "mysql_server": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    })

    # Fetch available MCP tools
    tools = await client.get_tools()

    # Create streaming model
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

    SYSTEM_PROMPT = """
    You are a database assistant that interacts with a MySQL MCP server.

    - Use `test_connection` to check database connectivity.
    - Use `list_tables` to inspect the schema.
    - Use `run_query` for SQL operations.
    
    Format your responses in **clear Markdown**, and wrap SQL queries inside ```sql code blocks.
    """

    # Initialize agent
    agent = create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT)

    # Markdown formatter
    def format_markdown(text: str) -> str:
        import re
        text = re.sub(r'###(\S)', r'### \1', text)
        text = re.sub(r'(### )', r'\n\1', text)
        text = re.sub(r'-([^\s])', r'- \1', text)
        text = re.sub(r'\*\*(\S)', r'** \1', text)
        text = re.sub(r'(\S)\*\*', r'\1 **', text)
        return text.strip()

    # Stream formatted chunks
    async for event in agent.astream_events({"messages": [{"role": "user", "content": query}]}):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"].content
            formatted = format_markdown(chunk)
            yield f"data: {formatted}\n\n"

    yield "data: [DONE]\n\n"
