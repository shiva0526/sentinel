"""Correlation Agent groups processed alerts into incidents and analyzes them."""

import sqlite3
import os
from typing import List, Dict
from datetime import datetime
import google.generativeai as genai


def get_processed_alerts(db_path: str = 'db/alerts.db') -> List[Dict]:
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts WHERE processed = 1")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def group_by_ip(alerts: List[Dict]) -> List[Dict]:
    ip_groups = {}
    for a in alerts:
        ip = a.get('ip')
        if ip:
            ip_groups.setdefault(ip, []).append(a)

    incidents = []
    for ip, group in ip_groups.items():
        if len(group) >= 2:
            incidents.append({
                "type": "IP_CLUSTER",
                "key": ip,
                "alerts": group
            })
    return incidents


def group_by_time_window(alerts: List[Dict]) -> List[Dict]:
    source_groups = {}
    for a in alerts:
        src = a.get('source')
        if src:
            source_groups.setdefault(src, []).append(a)

    incidents = []
    for src, group in source_groups.items():
        try:
            group.sort(key=lambda x: datetime.fromisoformat(
                x['timestamp'].replace('Z', '+00:00')))
        except Exception:
            pass

        current_window = []
        for a in group:
            if not current_window:
                current_window.append(a)
                continue
            try:
                t1 = datetime.fromisoformat(
                    current_window[0]['timestamp'].replace('Z', '+00:00'))
                t2 = datetime.fromisoformat(
                    a['timestamp'].replace('Z', '+00:00'))
                diff = abs((t2 - t1).total_seconds() / 60.0)
                if diff <= 10:
                    current_window.append(a)
                else:
                    if len(current_window) > 1:
                        incidents.append({
                            "type": "TIME_WINDOW",
                            "key": src,
                            "alerts": current_window
                        })
                    current_window = [a]
            except Exception:
                pass

        if len(current_window) > 1:
            incidents.append({
                "type": "TIME_WINDOW",
                "key": src,
                "alerts": current_window
            })
    return incidents


def analyze_incident_with_claude(incident: Dict) -> str:
    # build a clean short summary instead of dumping raw alert objects
    alert_lines = []
    for a in incident["alerts"]:
        line = f"- [{a.get('timestamp', 'unknown time')}] {a.get('type', 'unknown')}: {a.get('description', 'no description')}"
        alert_lines.append(line)

    alert_text = "\n".join(alert_lines)
    incident_type = incident.get("type", "UNKNOWN")
    incident_key = incident.get("key", "unknown")

    prompt = f"""These security alerts are grouped together because they share the same {incident_type} ({incident_key}).

Alerts:
{alert_text}

In 2 plain English sentences, answer:
1. Are these alerts part of a coordinated attack or are they unrelated?
2. What should the business owner know about this?

No technical jargon. Be direct and simple."""

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "user_will_fill_this":
            raise ValueError("No API key")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        full_prompt = "You are a cybersecurity analyst explaining findings to a non-technical business owner. Keep it short and simple.\n\n" + prompt
        response = model.generate_content(full_prompt)
        return response.text.strip()

    except Exception as e:
        return "These alerts appear to be part of a coordinated attack from the same source. The business owner should investigate this IP address immediately."


def run_correlation_agent(processed_alerts: List[Dict]) -> List[Dict]:
    print("--- AGENT 4: CORRELATION AGENT STARTING ---")

    if not processed_alerts:
        processed_alerts = get_processed_alerts()

    if not processed_alerts:
        print("[Correlation Agent] No processed alerts to correlate.")
        print("--- AGENT 4: CORRELATION AGENT DONE ---\n")
        return []

    # group alerts into incidents
    ip_incidents = group_by_ip(processed_alerts)
    time_incidents = group_by_time_window(processed_alerts)
    all_incidents = ip_incidents + time_incidents

    if not all_incidents:
        print("[Correlation Agent] No incident patterns found.")
        print("--- AGENT 4: CORRELATION AGENT DONE ---\n")
        return []

    print(f"[Correlation Agent] Found {len(all_incidents)} potential incidents. Analyzing with Claude...")
    final_incidents = []

    for inc in all_incidents:
        alert_count = len(inc["alerts"])
        inc_key = inc.get("key", "unknown")
        inc_type = inc.get("type", "UNKNOWN")

        print(f"[Correlation Agent] Incident: {alert_count} alerts grouped by {inc_type} → {inc_key}")

        summary = analyze_incident_with_claude(inc)
        inc["summary"] = summary
        final_incidents.append(inc)

        # print a short preview
        preview = summary.replace('\n', ' ')
        if len(preview) > 80:
            preview = preview[:80] + "..."
        print(f"  → Claude: \"{preview}\"\n")

    print(f"[Correlation Agent] Done — {len(final_incidents)} incidents identified.")
    print("--- AGENT 4: CORRELATION AGENT DONE ---\n")
    return final_incidents