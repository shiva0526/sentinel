"""Ingestion Agent loads existing alerts and attack output into a SQLite database."""

import sqlite3
import json
import os
from typing import List, Dict

def init_db(db_path: str = 'db/alerts.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            type TEXT,
            source TEXT,
            ip TEXT,
            user TEXT,
            description TEXT,
            timestamp TEXT,
            raw_severity TEXT,
            verdict TEXT,
            explanation TEXT,
            remediation TEXT,
            processed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def insert_alerts(alerts: List[Dict], db_path: str = 'db/alerts.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    count = 0
    for a in alerts:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO alerts 
                (id, type, source, ip, user, description, timestamp, raw_severity, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (a.get('id'), a.get('type'), a.get('source'), a.get('ip'), a.get('user'), a.get('description'), a.get('timestamp'), a.get('raw_severity')))
            if cursor.rowcount > 0: count += 1
        except Exception: pass
    conn.commit()
    conn.close()
    return count

def get_unprocessed_alerts(db_path: str = 'db/alerts.db') -> List[Dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts WHERE processed = 0")
    rows = cursor.fetchall()
    alerts = [dict(r) for r in rows]
    conn.close()
    return alerts

def run_ingestion_agent(attack_alerts: List[Dict]) -> List[Dict]:
    print("--- AGENT 2: INGESTION AGENT STARTING ---")
    db_path = os.path.join('db', 'alerts.db')
    try:
        init_db(db_path)
        print("[Ingestion Agent] Database ready.")
    except Exception as e:
        print(f"[Ingestion Agent] Error initializing DB: {e}")
        return []

    insert_alerts(attack_alerts, db_path)
    print(f"[Ingestion Agent] Loaded {len(attack_alerts)} alerts from attack agent.")

    fake_alerts_path = os.path.join('data', 'fake_alerts.json')
    fake_alerts = []
    if os.path.exists(fake_alerts_path):
        try:
            with open(fake_alerts_path, 'r', encoding='utf-8') as f:
                fake_alerts = json.load(f)
            insert_alerts(fake_alerts, db_path)
            print(f"[Ingestion Agent] Loaded {len(fake_alerts)} alerts from fake_alerts.json.")
        except Exception:
            pass

    unprocessed = get_unprocessed_alerts(db_path)
    print(f"[Ingestion Agent] {len(unprocessed)} alerts waiting for investigation.")
    print("--- AGENT 2: INGESTION AGENT DONE ---\n")
    return unprocessed
