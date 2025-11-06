from mcp.server.fastmcp import FastMCP
import pymysql

# Create MCP Server
mcp = FastMCP("MySQL MCP Server")

# ---------- DATABASE CONFIG ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",  # 🔒 Replace with your MySQL password
    "database": "mcp_test",  # e.g. 'test_db'
}

def get_connection():
    """Create a MySQL connection"""
    return pymysql.connect(**DB_CONFIG)


# ---------- MCP TOOLS ----------
@mcp.tool()
async def test_connection() -> str:
    """Simple tool to test DB connection"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT NOW();")
            result = cursor.fetchone()
        conn.close()
        return f"✅ MySQL Connected Successfully! Server Time: {result[0]}"
    except Exception as e:
        return f"❌ Connection failed: {e}"


@mcp.tool()
def list_tables() -> list:
    """List all tables in the database"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        return [f"Error: {e}"]


@mcp.tool()
def run_query(query: str) -> list:
    """Execute a custom SQL query (read-only recommended)"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        return [f"Error: {e}"]


# ---------- RUN MCP SERVER ----------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # or use transport="http" for network access
