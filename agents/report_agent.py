"""Report Agent generates a plain English morning report using Claude."""

import os
import json
from typing import List, Dict
import google.generativeai as genai

def run_report_agent(alerts: List[Dict], incidents: List[Dict]) -> str:
    print("--- AGENT 5: REPORT AGENT STARTING ---")
    
    prompt = f"""You are writing a security morning report for a small business owner with no technical background. Write in plain English. No jargon. Be specific and actionable.
Here are the alerts from last night: {json.dumps(alerts, indent=2)}
Here are the correlated incidents: {json.dumps(incidents, indent=2)}
Write a report with three sections:
Section 1 — CRITICAL THREATS
Section 2 — THINGS TO WATCH
Section 3 — FALSE POSITIVES DISMISSED
"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "user_will_fill_this":
            raise ValueError("No API key")
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        full_prompt = "You are writing a security report for a small business owner with no technical background. Write in plain English. No jargon. Be specific and actionable.\n\n" + prompt
        response = model.generate_content(full_prompt)
        report_content = response.text.strip()
    except Exception as e:
        report_content = "Mock Report... Add valid Gemini API key to see actual report content."
        
    try:
        os.makedirs('db', exist_ok=True)
        with open(os.path.join('db', 'report.txt'), 'w', encoding='utf-8') as f:
            f.write(report_content)
        print("[Report Agent] Morning report generated and saved to db/report.txt")
    except Exception as e: pass
        
    print("--- AGENT 5: REPORT AGENT DONE ---\n")
    return report_content
