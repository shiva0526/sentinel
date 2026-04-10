"""
Notification Agent - Alerts the website owner and provides fix instructions via MCP.
"""

import asyncio
import os
import sys
from typing import List, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["sentinel_mcp_server.py"],
    env=os.environ.copy()
)

async def send_owner_alerts(critical_alerts: List[Dict]):
    if not critical_alerts:
        return

    print(f"\n[📣 NOTIFICATION] Preparing urgent alerts for website owner...")
    
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            for alert in critical_alerts:
                msg = f"SECURITY ALERT: {alert['type']} detected!\n"
                msg += f"Description: {alert['description']}\n"
                msg += f"Urgency: CRITICAL\n"
                msg += f"Recommended Fix: {alert.get('explanation', 'Isolate host and investigate immediately.')}"
                
                print(f"[NOTIFICATION] Sending alert for {alert['type']} via MCP...")
                await session.call_tool("send_notification", {
                    "recipient": "owner@sentinel-protected-site.com",
                    "message": msg,
                    "priority": "CRITICAL"
                })

def run_notification_agent(alerts: List[Dict]):
    criticals = [a for a in alerts if a.get('verdict') == 'CRITICAL']
    if criticals:
        try:
            asyncio.run(send_owner_alerts(criticals))
        except Exception as e:
            print(f"[Notification Agent] Error: {e}")
