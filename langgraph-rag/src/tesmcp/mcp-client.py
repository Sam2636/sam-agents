import os
import asyncio
import gradio as gr
from fastmcp import Client

# ------------------ MCP Client ------------------
MCP_SERVER_URL = "server.py"  # MCP server HTTP URL
client = Client(MCP_SERVER_URL)

async def ping_mcp(message: str) -> str:
    """Ping MCP server: list tools to verify connection"""
    try:
        async with client:
            tools = await client.list_tools()
            print(f"Available tools: {tools}")

            tool_names = [tool["name"] for tool in tools]
            return f"✅ Connected to MCP!\nAvailable tools: {tool_names}"
    except Exception as e:
        return f"❌ MCP connection failed: {e}"

# ------------------ Gradio Chat ------------------
def chat_fn(message, chat_history=None):
    """Handle Gradio chat messages"""
    response = asyncio.run(ping_mcp(message))
    if chat_history is None:
        chat_history = []
    chat_history.append((message, response))
    return chat_history, chat_history

# ------------------ Launch Gradio ------------------
if __name__ == "__main__":
    with gr.Blocks() as app:
        gr.Markdown("### 💬 MCP Chat Handshake Test")
        gr.ChatInterface(fn=chat_fn, title="MCP Handshake Test")

    app.launch(server_name="127.0.0.1", server_port=7860)
