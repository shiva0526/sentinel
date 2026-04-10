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
    vt_malicious: int
    vt_suspicious: int
    verdict: str
    explanation: str
    confidence: str

def fetch_vt_data(ip: str) -> tuple:
    """Returns (vt_summary_str, malicious_count, suspicious_count)"""
    if not ip:
        return ("No IP address provided", 0, 0)
    api_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not api_key or api_key == "user_will_fill_this":
        return ("VirusTotal: Mocked (no real API key configured)", 0, 0)

    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 429:
            print("  -> VirusTotal rate limited, waiting 15 seconds...")
            time.sleep(15)
            response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            summary = f"{malicious} engines flagged as malicious, {suspicious} suspicious"
            return (summary, malicious, suspicious)
        else:
            return ("VirusTotal lookup failed", 0, 0)
    except Exception:
        return ("VirusTotal lookup error", 0, 0)

def vt_node(state: AgentState) -> dict:
    ip = state["alert"].get("ip")
    vt_summary, vt_malicious, vt_suspicious = fetch_vt_data(ip)
    state["vt_data"] = vt_summary
    state["vt_malicious"] = vt_malicious
    state["vt_suspicious"] = vt_suspicious
    return {"vt_data": vt_summary, "vt_malicious": vt_malicious, "vt_suspicious": vt_suspicious}

def decide_node(state: AgentState) -> dict:
    return {}

def fallback_analyze(alert: Dict, vt_malicious: int, vt_suspicious: int) -> tuple:
    """Enhanced heuristic analysis when API is not available."""
    alert_type = alert.get("type", "").lower()
    raw_severity = alert.get("raw_severity", "").lower()
    description = alert.get("description", "").lower()
    
    # Pattern-based verdict scoring (0-100, higher = more critical)
    critical_score = 0
    confidence = "LOW"
    
    # Alert type analysis - separate critical patterns
    critical_exact = ["malware_detected", "ransomware", "trojan", "worm", "data_exfiltration", "new_admin_account", "privilege_escalation", "persistence", "lateral_movement"]
    critical_keywords = ["malware", "ransomware", "trojan", "exploit", "injection", "rce", "code_execution", "credential_theft", "account_takeover"]
    suspicious_keywords = ["suspicious", "anomaly", "unusual", "unauthorized", "breach", "intrusion", "failed_login", "port_scan"]
    benign_keywords = ["healthcheck", "backup", "routine", "scheduled", "internal", "monitoring", "health_check"]
    
    if any(exact == alert_type for exact in critical_exact):
        critical_score += 90
        confidence = "HIGH"
    elif any(kw in alert_type for kw in critical_keywords):
        critical_score += 85
        confidence = "HIGH"
    elif any(kw in alert_type for kw in suspicious_keywords):
        critical_score += 45
        confidence = "MEDIUM"
    elif any(kw in alert_type for kw in benign_keywords):
        critical_score -= 50
        confidence = "HIGH"
    
    # Severity escalation with better mapping
    if raw_severity == "critical":
        critical_score += 45
    elif raw_severity == "high":
        critical_score += 25
    elif raw_severity == "medium":
        critical_score += 10
    elif raw_severity == "low":
        critical_score -= 5
    
    # VirusTotal integration with better thresholds
    if vt_malicious >= 15:
        critical_score += 60
        confidence = "HIGH"
    elif vt_malicious >= 10:
        critical_score += 50
        confidence = "HIGH"
    elif vt_malicious >= 5:
        critical_score += 30
        confidence = "MEDIUM"
    elif vt_malicious >= 1:
        critical_score += 15
    
    if vt_suspicious >= 10:
        critical_score += 25
    elif vt_suspicious >= 5:
        critical_score += 15
    
    # Description patterns - attack indicators
    critical_patterns = ["compromise", "stolen", "exfiltration", "ransomware", "encrypted", "locked"]
    suspicious_patterns = ["attack", "exploit", "scanning", "enumeration", "reconnaissance"]
    benign_patterns = ["safe", "clean", "verified", "whitelisted", "compliant", "passed"]
    
    if any(pattern in description for pattern in critical_patterns):
        critical_score += 35
    if any(pattern in description for pattern in suspicious_patterns):
        critical_score += 20
    if any(pattern in description for pattern in benign_patterns):
        critical_score -= 40
    
    # Determine verdict with adjusted thresholds
    if critical_score >= 85:
        verdict = "CRITICAL"
        if confidence == "LOW":
            confidence = "MEDIUM"
    elif critical_score >= 40:
        verdict = "SUSPICIOUS"
        if confidence == "LOW":
            confidence = "MEDIUM"
    elif critical_score <= -35:
        verdict = "FALSE_POSITIVE"
        if confidence == "LOW":
            confidence = "MEDIUM"
    else:
        verdict = "SUSPICIOUS"
    
    # Generate explanation based on verdict and evidence
    if verdict == "CRITICAL":
        if "malware" in alert_type:
            explanation = f"Malware detected on system - immediate action required."
        elif "exfiltration" in alert_type:
            explanation = f"Data exfiltration attempt detected - data loss likely."
        elif "new_admin" in alert_type:
            explanation = f"Unauthorized admin account creation detected - possible privilege escalation."
        else:
            explanation = f"Critical security threat identified: {alert.get('type')} with severity {raw_severity}."
    elif verdict == "FALSE_POSITIVE":
        explanation = f"Alert appears to be routine activity ({alert.get('type')}). No threat indicators found."
    else:
        vt_info = f"found {vt_malicious} threats" if vt_malicious > 0 else "no threats found"
        explanation = f"Alert requires investigation: {alert.get('type')} - VirusTotal {vt_info}."
    
    return verdict, explanation, confidence

def decide_node(state: AgentState) -> dict:
    return {}

def analyze_node(state: AgentState) -> dict:
    alert = state["alert"]
    vt_str = state.get("vt_data", "No VirusTotal data")
    vt_malicious = state.get("vt_malicious", 0)
    vt_suspicious = state.get("vt_suspicious", 0)

    sys_prompt = """You are a senior cybersecurity threat analyst with 15+ years of experience.
Your job is to investigate security alerts and provide accurate, actionable verdicts.
Base your analysis on alert characteristics, threat intelligence, and security best practices.
Always be precise and explain your reasoning clearly."""

    user_prompt = f"""Analyze this security alert and provide a verdict.

ALERT DETAILS:
- Alert ID: {alert.get('id')}
- Type: {alert.get('type')}
- Description: {alert.get('description')}
- Source: {alert.get('source')}
- IP Address: {alert.get('ip', 'N/A')}
- User Affected: {alert.get('user', 'N/A')}
- Raw Severity: {alert.get('raw_severity')}
- Timestamp: {alert.get('timestamp')}

THREAT INTELLIGENCE REPORT:
- VirusTotal: {vt_str}
- Malicious Detections: {vt_malicious}
- Suspicious Detections: {vt_suspicious}

ANALYSIS INSTRUCTIONS:
1. Evaluate the alert type and description for known attack patterns
2. Consider VirusTotal Intelligence: 10+ malicious = highly reliable threat, 5+ = concerning, 0-4 = low signal
3. Factor in raw severity level as an indicator
4. Assess false positive likelihood (routine internal services, health checks, etc.)

VERDICT DETERMINATION:
- CRITICAL: Strong indicators of active threat (malware, RCE, data exfiltration, compromised account)
- SUSPICIOUS: Multiple indicators or unusual behavior requiring investigation
- FALSE_POSITIVE: Routine activity, known safe operation, or benign alert

Respond EXACTLY in this format (no extra text):
VERDICT: [CRITICAL|SUSPICIOUS|FALSE_POSITIVE]
CONFIDENCE: [HIGH|MEDIUM|LOW]
REASONING: [Brief explanation of threat assessment]
EXPLANATION: [One sentence of clear, non-technical summary]
"""

    try:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key == "user_will_fill_this":
            raise ValueError("No Gemini API key configured")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro-latest")
        
        response = model.generate_content(sys_prompt + "\n\n" + user_prompt)
        content = response.text

        # Parse response with better error handling
        verdict = "SUSPICIOUS"
        confidence = "LOW"
        explanation = "Unable to determine from AI response."

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
            elif line.startswith("CONFIDENCE:"):
                raw = line.replace("CONFIDENCE:", "").strip().upper()
                if raw in ["HIGH", "MEDIUM", "LOW"]:
                    confidence = raw
            elif line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()

        return {"verdict": verdict, "explanation": explanation, "confidence": confidence}

    except Exception as e:
        # Use enhanced fallback heuristics
        verdict, explanation, confidence = fallback_analyze(alert, vt_malicious, vt_suspicious)
        return {"verdict": verdict, "explanation": explanation, "confidence": confidence}


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
            "vt_malicious": 0,
            "vt_suspicious": 0,
            "verdict": "",
            "explanation": "",
            "confidence": ""
        }

        try:
            result = investigate_app.invoke(initial_state)
            verdict = result.get("verdict", "SUSPICIOUS")
            explanation = result.get("explanation", "No explanation.")
            confidence = result.get("confidence", "LOW")
            print(f"  [API] VirusTotal: {result.get('vt_data', 'N/A')}")
        except Exception as e:
            verdict = "SUSPICIOUS"
            explanation = str(e)
            confidence = "LOW"
            print(f"  [Error] During investigation: {e}")

        print(f"  [Verdict] {verdict} ({confidence} confidence)")
        print(f"  [Info] {explanation}\n")

        alert["verdict"] = verdict
        alert["explanation"] = explanation
        alert["processed"] = 1
        investigated.append(alert)

        # ---- DB PERSISTENCE ----
        try:
            cursor.execute(
                "UPDATE alerts SET verdict=?, explanation=?, processed=1 WHERE id=?",
                (verdict, explanation, alert["id"])
            )
            conn.commit()
        except Exception as e:
            print(f"  -> DB save error: {e}")

    try:
        conn.close()
    except Exception:
        pass

    critical = len([a for a in investigated if a["verdict"] == "CRITICAL"])
    false_pos = len([a for a in investigated if a["verdict"] == "FALSE_POSITIVE"])
    suspicious = len([a for a in investigated if a["verdict"] == "SUSPICIOUS"])

    print(f"[Investigation Agent] Done - {critical} critical, {suspicious} suspicious, {false_pos} false positives.")
    print("--- AGENT 3: INVESTIGATION AGENT DONE ---\n")
    return investigated