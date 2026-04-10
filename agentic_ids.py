import re
import random
import datetime
import urllib.parse
import asyncio
import os
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import urllib.parse
import asyncio
import os
import sys
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ----------------- MCP CONFIG -----------------
SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["sentinel_mcp_server.py"],
    env=os.environ.copy()
)

async def call_mcp(tool_name: str, arguments: dict):
    """Utility to call MCP Tools."""
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text if result.content else ""

# ----------------- BASE IDS MODULES -----------------

class URLAnalyzer:
    def analyze(self, url: str) -> Dict[str, Any]:
        print(f"[*] Analyzing URL: {url}")
        parsed = urllib.parse.urlparse(url)
        length = len(url)
        has_https = parsed.scheme == "https"
        special_chars = len(re.findall(r'[@!#$%^&*.?]', url))
        suspicious_keywords = ['login', 'verify', 'update', 'secure', 'account', 'banking', 'admin', 'exec']
        has_suspicious_keywords = any(kw in url.lower() for kw in suspicious_keywords)
        
        risk_score = 0
        if length > 75: risk_score += 20
        if not has_https: risk_score += 30
        if special_chars > 5: risk_score += 20
        if has_suspicious_keywords: risk_score += 30
            
        return {
            "url": url,
            "length": length,
            "has_https": has_https,
            "special_chars": special_chars,
            "risk_score": risk_score
        }

class TrafficSimulator:
    def capture(self, dest_url: str) -> Dict[str, Any]:
        print("[*] Simulating Network Traffic Capture...")
        is_bad = "vuln" in dest_url or "phish" in dest_url or "admin" in dest_url
        packet_size = random.randint(100, 1500) if not is_bad else random.randint(3000, 8000)
        protocol_type = 6  # TCP
        src_ip = f"192.168.1.{random.randint(1,255)}"
        dst_ip = f"{random.randint(10,200)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        payload_entropy = random.uniform(3.0, 5.0) if not is_bad else random.uniform(6.5, 8.0)
        
        return {
            "src_ip": src_ip, "dst_ip": dst_ip,
            "packet_size": packet_size, "protocol_type": protocol_type,
            "payload_entropy": payload_entropy
        }

class MLTrafficClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        X_normal = np.array([[500, 6, 4.0], [1200, 6, 4.5], [200, 17, 3.2], [1500, 6, 4.9]])
        y_normal = np.zeros(len(X_normal))
        X_malicious = np.array([[8000, 6, 7.5], [4500, 6, 7.2], [9000, 17, 7.9], [6000, 6, 6.8]])
        y_malicious = np.ones(len(X_malicious))
        self.model.fit(np.vstack((X_normal, X_malicious)), np.concatenate((y_normal, y_malicious)))
        
    def predict(self, traffic_data: Dict[str, Any]) -> str:
        features = np.array([[traffic_data["packet_size"], traffic_data["protocol_type"], traffic_data["payload_entropy"]]])
        verdict = "MALICIOUS" if self.model.predict(features)[0] == 1 else "NORMAL"
        print(f"[*] ML Traffic Analysis: {verdict} (Entropy: {traffic_data['payload_entropy']:.2f})")
        return verdict


# ----------------- ADVANCED AGENTIC MODULES (MCP INTEGRATED) -----------------

class RedTeamSandboxAgent:
    """Autonomously verifies threats via MCP Sandbox."""
    async def verify_exploit(self, url: str) -> bool:
        print("[AGENT: RedTeam] Requesting MCP Sandbox Verification...")
        result = await call_mcp("verify_sandbox", {"url": url})
        print(f"[AGENT: RedTeam] Sandbox Results: {result}")
        return "INFECTION" in result

class DeceptionHoneypotAgent:
    """Uses MCP to redirect traffic."""
    async def deploy_honeypot(self, ip: str) -> Dict[str, str]:
        print(f"[AGENT: Deception] Requesting MCP Redirection for {ip}...")
        result = await call_mcp("deploy_honeypot", {"ip": ip})
        print(f"[AGENT: Deception] MCP Result: {result}")
        tactics = random.choice(["Port Scanning", "SQL Injection", "Directory Traversal"])
        return {"ip": ip, "tactics_extracted": tactics, "honeypot_status": "ACTIVE"}

class FirewallPolicyAgent:
    """Uses MCP to update WAF rules."""
    async def generate_rule(self, url: str, tactics: str) -> str:
        print("[AGENT: Firewall] Generating WAF rule via MCP...")
        rule = f"BLOCK {tactics} payload targeting {urllib.parse.urlparse(url).path}"
        result = await call_mcp("update_waf_rule", {"rule": rule})
        print(f"[AGENT: Firewall] MCP Result: {result}")
        return rule

class EmployeeNegotiationAgent:
    def interrogate_user(self, ip: str) -> bool:
        print(f"[AGENT: HR Negotation] Pinging employee via Slack...")
        response = random.choice(["Yes, it was me.", "No, not me."])
        print(f"[AGENT: HR Negotation] Response: '{response}'")
        return "yes" in response.lower()

class ProactiveThreatHunterAgent:
    def hunt(self):
        print("\n[AGENT: ThreatHunter] Proactive background sweep initiated...")
        return "APT_DORMANT" if random.random() > 0.8 else None


# ----------------- DECISION & RESPONSE -----------------

class AgenticDecisionEngine:
    def __init__(self):
        self.red_team = RedTeamSandboxAgent()
        self.negotiator = EmployeeNegotiationAgent()
        self.honeypot = DeceptionHoneypotAgent()
        
    async def decide_async(self, url: str, url_risk: int, traffic_verdict: str, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        print("\n[*] Agentic Decision Engine: Fusing Intelligence via MCP...")
        base_risk = url_risk + (50 if traffic_verdict == "MALICIOUS" else 0)
        risk_score = min(100, base_risk)
        
        action, severity, honeypot_data = "ALLOW", "LOW", None
        
        if risk_score >= 80:
            severity = "CRITICAL"
            if await self.red_team.verify_exploit(url):
                action = "DEPLOY_HONEYPOT_AND_BLOCK"
                honeypot_data = await self.honeypot.deploy_honeypot(traffic_data["dst_ip"])
            else:
                action, severity = "ALLOW", "FALSE_POSITIVE"
        elif risk_score >= 50:
            severity = "HIGH"
            if self.negotiator.interrogate_user(traffic_data["src_ip"]):
                action, severity = "ALLOW_AND_LOG", "LOW_INTERNAL"
            else:
                action = "ALERT_AND_MONITOR"
            
        return {
            "final_risk_score": risk_score,
            "action": action,
            "severity": severity,
            "honeypot_data": honeypot_data,
            "timestamp": datetime.datetime.now().isoformat()
        }

class ResponseModule:
    def __init__(self):
        self.firewall_agent = FirewallPolicyAgent()
        
    async def act_async(self, decision: Dict[str, Any], url: str, traffic_data: Dict[str, Any]):
        action = decision["action"]
        dst_ip = traffic_data["dst_ip"]
        
        print(f"\n--- EXECUTING MCP-MANAGED RESPONSE ---")
        if "BLOCK" in action:
            await call_mcp("block_ip", {"ip": dst_ip, "reason": "Verified malicious agentic trigger"})
            tactics = decision.get("honeypot_data", {}).get("tactics_extracted", "Unknown")
            await self.firewall_agent.generate_rule(url, tactics)
            
        print("[*] MCP Actions completed successfully.\n")

async def run_pipeline(url: str):
    print("\n===========================================================")
    print("   SENTINEL AI: MCP-ENHANCED AGENTIC SOC PIPELINE")
    print("===========================================================\n")
    
    # 1. Observe
    url_risks = URLAnalyzer().analyze(url)
    traffic = TrafficSimulator().capture(url)
    
    # 2. Analyze
    verdict = MLTrafficClassifier().predict(traffic)
    ProactiveThreatHunterAgent().hunt()
    
    # 3. Decide (Async MCP)
    decision = await AgenticDecisionEngine().decide_async(url, url_risks["risk_score"], verdict, traffic)
    
    # 4. Act (Async MCP)
    await ResponseModule().act_async(decision, url, traffic)
    return decision

def run_agentic_ids_pipeline(url: str):
    """Sync wrapper for the async pipeline."""
    return asyncio.run(run_pipeline(url))

if __name__ == "__main__":
    run_agentic_ids_pipeline("http://testphp.vulnweb.com/login.php?exec=1")
