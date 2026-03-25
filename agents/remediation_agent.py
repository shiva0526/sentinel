"""Remediation Agent generates fix instructions for critical alerts."""

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
        prompt = f"Fix instruction: Type: {alert.get('type')}, Desc: {alert.get('description')}"
        try:
            if not has_key: 
                raise ValueError("No API key")
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            full_prompt = "You are a cybersecurity expert giving fix instructions to a non-technical person. Be specific and simple. Maximum 5 steps.\n\n" + prompt
            response = model.generate_content(full_prompt)
            steps_text = response.text.strip()
            
            steps = [s.strip() for s in steps_text.split('\n') if s.strip()]
            remediations[alert['id']] = steps
            if conn:
                cursor.execute('UPDATE alerts SET remediation = ? WHERE id = ?', (json.dumps(steps), alert['id']))
                conn.commit()
        except Exception:
            remediations[alert['id']] = ["1. Isolate the affected machine.", "2. Contact your IT support immediately."]
            
    if conn: conn.close()
        
    print(f"[Remediation Agent] Fix steps generated for {len(critical_alerts)} critical alerts.")
    print("--- AGENT 6: REMEDIATION AGENT DONE ---\n")
    return remediations
