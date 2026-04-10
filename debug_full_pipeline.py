#!/usr/bin/env python
"""Full pipeline debug"""

import os
from agents.attack_agent import run_attack_agent
from agents.ingestion_agent import init_db, insert_alerts, get_unprocessed_alerts, run_ingestion_agent
from agents.investigation_agent import run_investigation_agent

url = "https://www.akashbhumi.com/"
db_path = os.path.join('db', 'alerts.db')

# Clean database
if os.path.exists(db_path):
    os.remove(db_path)
    print("Cleaned old database\n")

print("STEP 1: Attack Agent")
print("-" * 40)
attack_alerts = run_attack_agent(url)
print(f"Attack alerts generated: {len(attack_alerts)}\n")

print("STEP 2: Ingestion Agent")
print("-" * 40)
unprocessed = run_ingestion_agent(attack_alerts)
print(f"Unprocessed alerts from ingestion: {len(unprocessed)}\n")

if unprocessed:
    print("STEP 3: Investigation Agent")
    print("-" * 40)
    investigated = run_investigation_agent(unprocessed)
    print(f"Investigated alerts: {len(investigated)}")
    
    critical = sum(1 for a in investigated if a.get('verdict') == 'CRITICAL')
    suspicious = sum(1 for a in investigated if a.get('verdict') == 'SUSPICIOUS')
    fp = sum(1 for a in investigated if a.get('verdict') == 'FALSE_POSITIVE')
    
    print(f"\nVerdicts: {critical} critical, {suspicious} suspicious, {fp} false positives")
else:
    print("ERROR: No alerts in ingestion stage!")
    print("\nDEBUG: Check database directly...")
    init_db(db_path)
    conn_check = __import__('sqlite3').connect(db_path)
    cursor = conn_check.cursor()
    cursor.execute("SELECT COUNT(*) FROM alerts")
    count = cursor.fetchone()[0]
    print(f"Database has {count} alerts")
    conn_check.close()
