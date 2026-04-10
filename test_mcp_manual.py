import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["sentinel_mcp_server.py"],
    env=os.environ.copy()
)

async def test():
    print("Testing MCP Connection...")
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected. Calling send_notification...")
            res = await session.call_tool("send_notification", {"recipient": "test@test.com", "message": "TEST ALERT"})
            print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(test())
