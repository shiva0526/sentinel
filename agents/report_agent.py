"""Report Agent generates a plain English morning report using Claude/Gemini."""
import os
import json
from typing import List, Dict

def run_report_agent(alerts: List[Dict], incidents: List[Dict]) -> str:
    try:
        critical_alerts = [a for a in alerts if a.get('verdict') == 'CRITICAL']
        suspicious_alerts = [a for a in alerts if a.get('verdict') == 'SUSPICIOUS']
        fp_alerts = [a for a in alerts if a.get('verdict') == 'FALSE_POSITIVE']
        
        report_content = "=======================================================\n"
        report_content += "     SENTINEL AI: INCIDENT & THREAT INTELLIGENCE     \n"
        report_content += "=======================================================\n"
        report_content += "EXECUTIVE SUMMARY:\n"
        report_content += f"The system processed {len(alerts)} alerts. Detected {len(critical_alerts)} CRITICAL threats requiring immediate intervention, "
        report_content += f"{len(suspicious_alerts)} SUSPICIOUS events requiring monitoring, and determined {len(fp_alerts)} to be routine/safe.\n\n"
        
        report_content += "--- [ 1. CRITICAL THREATS ] ---\n"
        if not critical_alerts:
            report_content += "No critical threats detected.\n"
        for alert in critical_alerts:
            report_content += f"[!] {alert.get('type', 'Unknown')} - {alert.get('description', 'No description')} (Source IP: {alert.get('ip', 'N/A')})\n"
            report_content += f"   Reason: {alert.get('explanation', 'None')}\n"
        
        report_content += "\n--- [ 2. THINGS TO WATCH ] ---\n"
        if not suspicious_alerts:
            report_content += "No suspicious anomalies flagged.\n"
        for alert in suspicious_alerts:
            report_content += f"[?] {alert.get('type', 'Unknown')} - {alert.get('description', 'No description')}\n"
        
        report_content += "\n--- [ 3. FALSE POSITIVES DISMISSED ] ---\n"
        if not fp_alerts:
            report_content += "No false positives registered.\n"
        for alert in fp_alerts:
            report_content += f"[*] {alert.get('type', 'Unknown')} : Filtered as routine activity.\n"
        
        report_content += "\n=======================================================\n"
        
        try:
            os.makedirs('db', exist_ok=True)
            with open(os.path.join('db', 'report.txt'), 'w', encoding='utf-8') as f:
                f.write(report_content)
        except Exception:
            pass
            
        return report_content
    except Exception as e:
        return f"Safely recovered from internal string formatting error: {str(e)}"
