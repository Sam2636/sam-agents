# from mcp.server.fastmcp import FastMCP

# mcp = FastMCP("My MCP Server")

# @mcp.tool()
# def say_hello(name: str) -> str:
#     return f"Hello, {name} from MCP!"

# @mcp.tool()
# def add(a: int, b: int) -> int:
#     return a + b

# @mcp.tool()
# def multiply(a: int, b: int) -> int:
#     return a * b

# if __name__ == "__main__":
#     mcp.run(transport="stdio")  # defaults to HTTP transport on 127.0.0.1:8000

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
def say_hello(name: str) -> str:
    return f"Hello, {name} from MCP!"

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    return a * b

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)  # <-- HTTP transport
