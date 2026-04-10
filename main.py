"""Main pipeline script for SentinelAI."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agents.attack_agent import run_attack_agent
from agents.ingestion_agent import run_ingestion_agent
from agents.investigation_agent import run_investigation_agent
from agents.correlation_agent import run_correlation_agent
from agents.report_agent import run_report_agent
from agents.remediation_agent import run_remediation_agent
from agentic_ids import run_agentic_ids_pipeline

def main():
    print("==================================================")
    print("   SENTINELAI — STARTING PIPELINE")
    print("==================================================\n")
    
    # Reset database to ensure fresh analysis
    db_path = os.path.join('db', 'alerts.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("[Main] Database reset for fresh analysis.\n")
        except:
            pass
    
    url = "http://testphp.vulnweb.com"
    if len(sys.argv) > 1:
        url = sys.argv[1]
        
    try: attack_alerts = run_attack_agent(url)
    except: attack_alerts = []
    
    try: unprocessed_alerts = run_ingestion_agent(attack_alerts)
    except: unprocessed_alerts = attack_alerts
    
    try: investigated_alerts = run_investigation_agent(unprocessed_alerts)
    except: investigated_alerts = unprocessed_alerts
    
    try: incidents = run_correlation_agent(investigated_alerts)
    except: incidents = []
    
    try: report = run_report_agent(investigated_alerts, incidents)
    except: pass
    
    try: remediations = run_remediation_agent(investigated_alerts)
    except: pass
    
    # ---------------------------------------------------------
    # NEW: Run Agentic Intrusion Detection & Response System
    # ---------------------------------------------------------
    try:
        ids_decision = run_agentic_ids_pipeline(url)
    except Exception as e:
        print(f"[Main] Error running agentic IDS pipeline: {e}")
        ids_decision = None
    
    total = len(investigated_alerts)
    critical = sum(1 for a in investigated_alerts if a.get('verdict') == 'CRITICAL')
    suspicious = sum(1 for a in investigated_alerts if a.get('verdict') == 'SUSPICIOUS')
    false_positives = sum(1 for a in investigated_alerts if a.get('verdict') == 'FALSE_POSITIVE')
    
    print("==================================================")
    print("   PIPELINE SUMMARY")
    print("==================================================")
    print(f"Total alerts processed : {total}")
    print(f"Critical threats       : {critical}")
    print(f"Suspicious             : {suspicious}")
    print(f"False positives        : {false_positives}")
    print("==================================================")
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
