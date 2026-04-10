"""
Self-Healing Agent - Detects errors/failures in the pipeline and takes corrective action via MCP.
"""

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

async def run_self_heal(failed_component: str, error_message: str):
    print(f"\n[!] SELF-HEAL: Error detected in {failed_component}!")
    print(f"[!] SELF-HEAL: Error Details: {error_message}")
    
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Simple heuristic decision engine for healing
            if "port" in error_message.lower() or "connection" in error_message.lower():
                print(f"[SELF-HEAL] Triggering service restart via MCP...")
                await session.call_tool("restart_service", {"service_name": "NetworkAnalytics"})
            
            elif "config" in error_message.lower() or "not found" in error_message.lower():
                print(f"[SELF-HEAL] Triggering config patch via MCP...")
                await session.call_tool("patch_config", {"file_path": "settings.yaml", "fix": "Resetting default paths"})
                
            else:
                print(f"[SELF-HEAL] Unknown error type. Performing general system health reset...")
                await session.call_tool("restart_service", {"service_name": "SentinelCore"})
                
    print("[SELF-HEAL] Corrective actions completed. Resuming pipeline flow.\n")

def trigger_healing(component: str, error: Exception):
    """Sync bridge to trigger async healing."""
    try:
        asyncio.run(run_self_heal(component, str(error)))
    except Exception as e:
        print(f"[SELF-HEAL] Fatal: Healing agent itself failed: {e}")
