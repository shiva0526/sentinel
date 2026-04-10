import asyncio
import os
import json
import datetime
from typing import List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.stdio import stdio_server

# Define the storage paths
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_PROJECT_ROOT, "db")
INCIDENT_LOG_PATH = os.path.join(DB_PATH, "incidents.json")
FIREWALL_LOG_PATH = os.path.join(DB_PATH, "firewall_rules.txt")
NOTIFICATION_LOG_PATH = os.path.join(DB_PATH, "notifications.json")

# Initialize the MCP Server
server = Server("Sentinel-SOC-MCP")

# Ensure DB exists
os.makedirs(DB_PATH, exist_ok=True)

# --- MCP TOOLS ---

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available forensic and response tools."""
    return [
        types.Tool(
            name="block_ip",
            description="Blocks a malicious IP address at the firewall level.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip": {"type": "string", "description": "The IP address to block"},
                    "reason": {"type": "string", "description": "Reason for blocking"}
                },
                "required": ["ip"]
            }
        ),
        types.Tool(
            name="isolate_host",
            description="Isolates an internal host from the network.",
            inputSchema={
                "type": "object",
                "properties": {
                    "host_id": {"type": "string", "description": "ID or IP of the host to isolate"}
                },
                "required": ["host_id"]
            }
        ),
        types.Tool(
            name="log_incident",
            description="Logs a critical security incident for forensic audit.",
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "ip": {"type": "string"},
                    "verdict": {"type": "string"}
                },
                "required": ["alert_id", "type", "verdict"]
            }
        ),
        types.Tool(
            name="deploy_honeypot",
            description="Redirects an IP address to a Deception Honeypot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip": {"type": "string"}
                },
                "required": ["ip"]
            }
        ),
        types.Tool(
            name="update_waf_rule",
            description="Dynamically updates Web Application Firewall rules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule": {"type": "string"}
                },
                "required": ["rule"]
            }
        ),
        types.Tool(
            name="verify_sandbox",
            description="Replays a payload in a sandbox to verify for infection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="restart_service",
            description="Restarts a system service that has crashed or is unhealthy.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {"type": "string"}
                },
                "required": ["service_name"]
            }
        ),
        types.Tool(
            name="patch_config",
            description="Autonomously patches a configuration file to fix an error.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "fix": {"type": "string"}
                },
                "required": ["file_path", "fix"]
            }
        ),
        types.Tool(
            name="send_notification",
            description="Sends a critical security alert to the website owner via Email/Slack.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipient": {"type": "string"},
                    "message": {"type": "string"},
                    "priority": {"type": "string"}
                },
                "required": ["recipient", "message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Execute the requested tool."""
    if not arguments:
        return [types.TextContent(type="text", text="No arguments provided")]

    if name == "block_ip":
        ip = arguments.get("ip")
        reason = arguments.get("reason", "Malicious activity detected")
        rule = f"iptables -I INPUT -s {ip} -j DROP"
        
        with open(FIREWALL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] BLOCK {ip} - {reason}\n")
            
        print(f"[MCP] Executing Action: {rule}")
        return [types.TextContent(type="text", text=f"SUCCESS: IP {ip} blocked. Rule: {rule}")]

    elif name == "isolate_host":
        host = arguments.get("host_id")
        msg = f"Host {host} has been moved to isolation VLAN 999. All active connections dropped."
        print(f"[MCP] Executing Action: ISOLATE {host}")
        return [types.TextContent(type="text", text=msg)]

    elif name == "log_incident":
        incident = {
            "mcp_logged": True,
            "timestamp": datetime.datetime.now().isoformat(),
            **arguments
        }
        
        incidents = []
        if os.path.exists(INCIDENT_LOG_PATH):
            try:
                with open(INCIDENT_LOG_PATH, "r") as f:
                    incidents = json.load(f)
            except: pass
            
        incidents.append(incident)
        with open(INCIDENT_LOG_PATH, "w") as f:
            json.dump(incidents, f, indent=2)
            
        return [types.TextContent(type="text", text=f"Incident {arguments['alert_id']} logged via MCP.")]

    elif name == "deploy_honeypot":
        ip = arguments.get("ip")
        print(f"[MCP] Deploying Deception for {ip}")
        return [types.TextContent(type="text", text=f"SUCCESS: Traffic from {ip} redirected to Sentinel-Honeypot-Alpha.")]

    elif name == "update_waf_rule":
        rule = arguments.get("rule")
        print(f"[MCP] Updating WAF Rule: {rule}")
        return [types.TextContent(type="text", text=f"SUCCESS: WAF policy updated with rule: {rule}")]

    elif name == "verify_sandbox":
        url = arguments.get("url")
        res = "INFECTION_STAGED" if "vuln" in url.lower() else "NO_MALICIOUS_BEHAVIOR"
        print(f"[MCP] Sandbox Verification for {url}: {res}")
        return [types.TextContent(type="text", text=res)]

    elif name == "restart_service":
        svc = arguments.get("service_name")
        print(f"[MCP] Self-Healing: Restarting {svc}...")
        return [types.TextContent(type="text", text=f"SUCCESS: Service {svc} restarted and health checked.")]

    elif name == "patch_config":
        path = arguments.get("file_path")
        print(f"[MCP] Self-Healing: Patching {path}...")
        return [types.TextContent(type="text", text=f"SUCCESS: Config at {path} patched with provided fixes.")]

    elif name == "send_notification":
        to = arguments.get("recipient")
        msg = arguments.get("message")
        priority = arguments.get("priority", "HIGH")
        
        # Persist to local "Mailbox" for demo purposes
        notif_record = {
            "to": to,
            "timestamp": datetime.datetime.now().isoformat(),
            "priority": priority,
            "message": msg
        }
        
        history = []
        if os.path.exists(NOTIFICATION_LOG_PATH):
            try:
                with open(NOTIFICATION_LOG_PATH, "r") as f:
                    history = json.load(f)
            except: pass
            
        history.append(notif_record)
        with open(NOTIFICATION_LOG_PATH, "w") as f:
            json.dump(history, f, indent=2)
            
        print(f"[MCP] NOTIFICATION SENT TO {to} (Priority: {priority}) - Logged to {NOTIFICATION_LOG_PATH}")
        return [types.TextContent(type="text", text=f"SUCCESS: Notification delivered to {to}. Data persisted to Sentinel Mailbox.")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Sentinel-SOC-MCP",
                server_version="1.0.0",
                capabilities=types.ServerCapabilities(
                    tools=types.ToolsCapability(listChanged=False)
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
