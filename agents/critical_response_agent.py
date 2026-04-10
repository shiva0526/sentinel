"""
Critical Response Agent - Now executes AI-suggested solutions via MCP.
"""
import os
import json
import datetime
import asyncio
import sys
from typing import Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["sentinel_mcp_server.py"],
    env=os.environ.copy()
)

async def call_mcp_action(tool_name: str, arguments: dict):
    print(f"  [MCP Execution] Triggering tool: {tool_name}")
    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  [MCP Result] {content.text}")
                return result
    except Exception as e:
        print(f"  [MCP Error] Tool {tool_name} failed: {e}")

def run_autonomous_solution(alert: Dict):
    """
    Executes the customized AI-generated solution for this specific alert.
    """
    ip = alert.get("ip", "N/A")
    # Fetch tools suggested by Remediation Agent
    suggested_tools = alert.get("mcp_tools", ["block_ip", "log_incident"])
    
    print(f"\n  === EXECUTING AI-GENERATED SOLUTION ===")
    print(f"  [*] Target      : {ip}")
    print(f"  [*] Action Plan : {suggested_tools}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        for tool in suggested_tools:
            # Map tool to required arguments
            args = {"ip": ip} # default
            if tool == "isolate_host": args = {"host_id": ip}
            if tool == "log_incident": args = {"alert_id": alert.get("id"), "type": alert.get("type"), "verdict": "CRITICAL"}
            if tool == "update_waf_rule": args = {"rule": f"BLOCK payload matching {alert.get('type')}"}
            if tool == "block_ip": args = {"ip": ip, "reason": "Autonomous mitigation"}
            if tool == "verify_sandbox": args = {"url": "http://malicious-sample.internal"}
            
            loop.run_until_complete(call_mcp_action(tool, args))
            
    finally:
        loop.close()

    print(f"  [SUCCESS] Autonomous mitigation complete.\n")
