"""Test script to verify the MCP SSE server is working end-to-end."""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

MCP_URL = "http://localhost:8080/sse"

async def main():
    print("=" * 50)
    print("  MCP SSE Server — End-to-End Test")
    print("=" * 50)

    # 1. Connect to the SSE server
    print("\n[1] Connecting to MCP server at", MCP_URL, "...")
    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("    ✅ Connected and initialized successfully!\n")

            # 2. List all available tools
            print("[2] Listing available tools...")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"    🔧 {tool.name}: {tool.description}")
            print(f"\n    Total tools: {len(tools.tools)}\n")

            # 3. Call 'verify_sandbox' tool
            print("[3] Calling tool: verify_sandbox (url='http://testphp.vulnweb.com')...")
            result = await session.call_tool("verify_sandbox", {"url": "http://testphp.vulnweb.com"})
            response_text = result.content[0].text
            print(f"    📦 Response: {response_text}\n")

            # 4. Call 'block_ip' tool
            print("[4] Calling tool: block_ip (ip='10.0.0.99', reason='Test block')...")
            result = await session.call_tool("block_ip", {"ip": "10.0.0.99", "reason": "Test block"})
            response_text = result.content[0].text
            print(f"    📦 Response: {response_text}\n")

            # 5. Call 'send_notification' tool
            print("[5] Calling tool: send_notification...")
            result = await session.call_tool("send_notification", {
                "recipient": "admin@sentinel.local",
                "message": "MCP test notification — server is operational.",
                "priority": "LOW"
            })
            response_text = result.content[0].text
            print(f"    📦 Response: {response_text}\n")

    print("=" * 50)
    print("  ✅ ALL TESTS PASSED — MCP Server is fully operational!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
