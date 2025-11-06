import asyncio
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# ---------- 1️⃣ Load OpenAI API Key ----------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env")

# ---------- 2️⃣ Define Context ----------
@dataclass
class SchemaContext:
    table_name: str


# ---------- 3️⃣ Async Main Function ----------
async def main():
    # --- MCP Server Config ---
    client = MultiServerMCPClient({
        "mysql_server": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",  # Your running MCP server
        }
    })

    # --- Fetch tools dynamically from the MCP server ---
    tools = await client.get_tools()

    # --- Initialize OpenAI model ---
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # --- Define system prompt ---
    SYSTEM_PROMPT = """
    You are a database assistant that interacts with a MySQL MCP server.
    - Use `test_connection` to check DB connectivity.
    - Use `list_tables` to inspect the schema..
    - Use `run_query` for custom SQL operations.
    Always display SQL queries in markdown ```sql blocks.
    """

    # --- Create LangChain Agent ---
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    # --- Ask the agent to test connection and list tables ---
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "Test DB connection and list all tables."}]
    })

    print("\n💬 Agent Output:\n", response)


# ---------- 4️⃣ Run the Client ----------
if __name__ == "__main__":
    asyncio.run(main())
