"""Investigation Agent analyzes alerts using LangGraph and Claude."""

import os
import time
import requests
import sqlite3
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
import google.generativeai as genai

class AgentState(TypedDict):
    alert: Dict
    vt_data: str
    verdict: str
    explanation: str
    confidence: str

def fetch_vt_data(ip: str) -> str:
    if not ip:
        return "0 engines flagged"
    api_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not api_key or api_key == "user_will_fill_this":
        return "43 engines flagged as malicious (Mocked)"

    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 429:
            print("  → VirusTotal rate limited, waiting 15 seconds...")
            time.sleep(15)
            response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            return f"{malicious} engines flagged as malicious, {suspicious} suspicious"
        else:
            return "0 engines flagged"
    except Exception:
        return "0 engines flagged"

def vt_node(state: AgentState) -> dict:
    ip = state["alert"].get("ip")
    vt_result = fetch_vt_data(ip)
    return {"vt_data": vt_result}

def decide_node(state: AgentState) -> dict:
    return {}

def analyze_node(state: AgentState) -> dict:
    alert = state["alert"]
    vt_str = state["vt_data"]

    sys_prompt = """You are a senior cybersecurity analyst. 
You investigate security alerts and give clear verdicts. 
Always respond in the exact format requested. Never deviate."""

    user_prompt = f"""Investigate this security alert and give a verdict.

ALERT TYPE: {alert.get('type')}
DESCRIPTION: {alert.get('description')}
IP ADDRESS: {alert.get('ip')}
USER AFFECTED: {alert.get('user')}
RAW SEVERITY: {alert.get('raw_severity')}
TIMESTAMP: {alert.get('timestamp')}

THREAT INTELLIGENCE: {vt_str}

VERDICT RULES — follow these exactly, do not ignore them:
- Use CRITICAL if ANY of these are true:
  * VirusTotal flagged 5 or more engines as malicious
  * Alert type is malware_detected
  * Alert type is failed_login with high frequency
  * Alert type is data_exfiltration
  * Alert type is new_admin_account created outside business hours

- Use FALSE_POSITIVE if ALL of these are true:
  * VirusTotal flagged 0 engines
  * Alert type is routine (cloudflare_healthcheck, routine_backup, known internal service)

- Use SUSPICIOUS for everything else that does not clearly fit CRITICAL or FALSE_POSITIVE

Respond in EXACTLY this format, no extra text:
VERDICT: CRITICAL
EXPLANATION: One plain English sentence with no jargon.
CONFIDENCE: HIGH

"""

    try:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key == "user_will_fill_this":
            raise ValueError("No API key")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = sys_prompt + "\n\n" + user_prompt
        response = model.generate_content(prompt)
        content = response.text

        # parse response
        verdict = "SUSPICIOUS"
        explanation = "Could not parse explanation."
        confidence = "LOW"

        for line in content.strip().split('\n'):
            line = line.strip()
            if line.startswith("VERDICT:"):
                raw = line.replace("VERDICT:", "").strip().upper()
                if "CRITICAL" in raw:
                    verdict = "CRITICAL"
                elif "FALSE_POSITIVE" in raw or "FALSE POSITIVE" in raw:
                    verdict = "FALSE_POSITIVE"
                else:
                    verdict = "SUSPICIOUS"
            elif line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                raw = line.replace("CONFIDENCE:", "").strip().upper()
                if raw in ["HIGH", "MEDIUM", "LOW"]:
                    confidence = raw

        return {"verdict": verdict, "explanation": explanation, "confidence": confidence}

    except Exception as e:
        alert_type = alert.get("type", "")
        if any(x in alert_type for x in ["malware", "exfiltration", "failed_login", "new_admin"]):
            verdict = "CRITICAL"
        elif any(x in alert_type for x in ["backup", "healthcheck"]):
            verdict = "FALSE_POSITIVE"
        else:
            verdict = "SUSPICIOUS"
        return {"verdict": verdict, "explanation": f"Fallback due to API error: {e}", "confidence": "LOW"}


# build the LangGraph workflow
workflow = StateGraph(AgentState)
workflow.add_node("vt_check", vt_node)
workflow.add_node("decide", decide_node)
workflow.add_node("analyze", analyze_node)
workflow.set_entry_point("vt_check")
workflow.add_edge("vt_check", "decide")
workflow.add_edge("decide", "analyze")
workflow.add_edge("analyze", END)
investigate_app = workflow.compile()


def run_investigation_agent(alerts: List[Dict]) -> List[Dict]:
    print("--- AGENT 3: INVESTIGATION AGENT STARTING ---")

    if not alerts:
        print("[Investigation Agent] No alerts to investigate.")
        print("--- AGENT 3: INVESTIGATION AGENT DONE ---\n")
        return []

    db_path = os.path.join('db', 'alerts.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception as e:
        print(f"[Investigation Agent] DB error: {e}")
        return []

    investigated = []

    for alert in alerts:
        print(f"[Investigation Agent] Investigating {alert['id']}: {alert['type']}")

        initial_state = {
            "alert": alert,
            "vt_data": "",
            "verdict": "",
            "explanation": "",
            "confidence": ""
        }

        try:
            result = investigate_app.invoke(initial_state)
            verdict = result.get("verdict", "SUSPICIOUS")
            explanation = result.get("explanation", "No explanation.")
            confidence = result.get("confidence", "LOW")
            vt_info = result.get("vt_data", "0 engines flagged")
            print(f"  → VirusTotal: {vt_info}")
        except Exception as e:
            verdict = "SUSPICIOUS"
            explanation = str(e)
            confidence = "LOW"
            print(f"  → Error during investigation: {e}")

        print(f"  → Verdict: {verdict} ({confidence} confidence)")
        print(f"  → {explanation}\n")

        alert["verdict"] = verdict
        alert["explanation"] = explanation
        alert["processed"] = 1
        investigated.append(alert)

        try:
            cursor.execute(
                "UPDATE alerts SET verdict=?, explanation=?, processed=1 WHERE id=?",
                (verdict, explanation, alert["id"])
            )
            conn.commit()
        except Exception as e:
            print(f"  → DB save error: {e}")

    try:
        conn.close()
    except Exception:
        pass

    critical = len([a for a in investigated if a["verdict"] == "CRITICAL"])
    false_pos = len([a for a in investigated if a["verdict"] == "FALSE_POSITIVE"])
    suspicious = len([a for a in investigated if a["verdict"] == "SUSPICIOUS"])

    print(f"[Investigation Agent] Done — {critical} critical, {suspicious} suspicious, {false_pos} false positives.")
    print("--- AGENT 3: INVESTIGATION AGENT DONE ---\n")
    return investigated