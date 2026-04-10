"""
Remediation Agent - Now with Autonomous Action Generation.
Finds solutions and suggests specific MCP tools to take action against critical threats.
"""
import sqlite3
import os
import json
from typing import List, Dict
import google.generativeai as genai

def run_remediation_agent(alerts: List[Dict]) -> Dict[str, List[str]]:
    print("--- AGENT 6: REMEDIATION AGENT STARTING ---")
    
    critical_alerts = [a for a in alerts if a.get('verdict') == 'CRITICAL']
    remediations = {}
    
    db_path = os.path.join('db', 'alerts.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception: conn = None

    api_key = os.getenv("GEMINI_API_KEY")
    has_key = api_key and api_key != "user_will_fill_this"
        
    for alert in critical_alerts:
        # Prompt for both Human steps and Autonomous MCP tools
        prompt = f"""
        Threat Detected: {alert.get('type')}
        Description: {alert.get('description')}
        
        Task:
        1. Find a solution for this threat (max 5 clear steps for a human).
        2. Identify which of these MCP tools should be TRIGGERED AUTONOMOUSLY: [block_ip, isolate_host, update_waf_rule, deploy_honeypot, verify_sandbox, restart_service]
        
        Respond in JSON format:
        {{
            "solution_steps": ["step1", "step2"],
            "suggested_mcp_tools": ["tool_name1", "tool_name2"]
        }}
        """
        
        try:
            if not has_key: raise ValueError("No key")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            
            # Simple parsing for JSON in markdown-y response
            txt = response.text.strip()
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0].strip()
            elif "{" in txt:
                txt = txt[txt.find("{"):txt.rfind("}")+1]
                
            data = json.loads(txt)
            steps = data.get("solution_steps", ["Isolate the host."])
            mcp_tools = data.get("suggested_mcp_tools", ["block_ip"])
            
            remediations[alert['id']] = steps
            alert["mcp_tools"] = mcp_tools # Store for Response agent
            
            if conn:
                cursor.execute('UPDATE alerts SET remediation = ? WHERE id = ?', (json.dumps(steps), alert['id']))
                conn.commit()
                
            print(f"  [Remediation] Found solution for {alert['id']}. Suggested Actions: {mcp_tools}")
            
        except Exception as e:
            print(f"  [Remediation] Falling back for {alert['id']}: {e}")
            remediations[alert['id']] = ["1. Isolate the affected machine.", "2. Contact IT Support."]
            alert["mcp_tools"] = ["block_ip", "isolate_host"]
            
    if conn: conn.close()
        
    print(f"[Remediation Agent] Solutions found and autonomous actions prepared for {len(critical_alerts)} threats.")
    print("--- AGENT 6: REMEDIATION AGENT DONE ---\n")
    return remediations
