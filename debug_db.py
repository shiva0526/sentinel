#!/usr/bin/env python
"""Check what's in the database after a scan"""

import os
import sqlite3
from agents.attack_agent import run_attack_agent
from agents.ingestion_agent import run_ingestion_agent

url = "https://www.akashbhumi.com/"
db_path = os.path.join('db', 'alerts.db')

# Clean database
if os.path.exists(db_path):
    os.remove(db_path)

attack_alerts = run_attack_agent(url)
print(f"Attack agent returned {len(attack_alerts)} alerts")
for alert in attack_alerts:
    print(f"  - {alert.get('id')}: {alert.get('type')}, processed={alert.get('processed', 'NOT_SET')}")

print("\nRunning ingestion agent...")
unprocessed = run_ingestion_agent(attack_alerts)
print(f"Ingestion returned {len(unprocessed)} unprocessed alerts")

print("\nDirect database query:")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, type, processed FROM alerts ORDER BY id")
rows = cursor.fetchall()
print(f"Total rows in DB: {len(rows)}")
for row in rows:
    print(f"  - {row[0]}: {row[1]}, processed={row[2]}")

cursor.execute("SELECT COUNT(*) FROM alerts WHERE processed = 0")
unproc_count = cursor.fetchone()[0]
print(f"\nUnprocessed alerts in DB: {unproc_count}")
conn.close()
