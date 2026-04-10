#!/usr/bin/env python
"""Test the improved model with a real website."""

from agents.attack_agent import run_attack_agent
from agents.ingestion_agent import run_ingestion_agent
from agents.investigation_agent import run_investigation_agent

url = "https://www.akashbhumi.com/"

print("=" * 60)
print(f"TESTING IMPROVED MODEL ON: {url}")
print("=" * 60 + "\n")

# Attack Agent
print("STEP 1: Attack Agent - Scanning for vulnerabilities...")
attack_alerts = run_attack_agent(url)
print(f"Found {len(attack_alerts)} potential vulnerabilities\n")

# Ingestion Agent
print("STEP 2: Ingestion Agent - Loading alerts into database...")
unprocessed = run_ingestion_agent(attack_alerts)
print(f"Total alerts ready for investigation: {len(unprocessed)}\n")

# Investigation Agent
print("STEP 3: Investigation Agent - Analyzing with improved heuristics...")
investigated = run_investigation_agent(unprocessed)

# Summary
print("\n" + "=" * 60)
print("ANALYSIS SUMMARY")
print("=" * 60)
critical = sum(1 for a in investigated if a.get('verdict') == 'CRITICAL')
suspicious = sum(1 for a in investigated if a.get('verdict') == 'SUSPICIOUS')
false_pos = sum(1 for a in investigated if a.get('verdict') == 'FALSE_POSITIVE')

print(f"Total alerts analyzed: {len(investigated)}")
print(f"Critical threats: {critical}")
print(f"Suspicious: {suspicious}")
print(f"False positives: {false_pos}")

print("\nDETAILED RESULTS:")
print("-" * 60)
for alert in investigated:
    verdict = alert.get('verdict', 'UNKNOWN')
    alert_type = alert.get('type', 'unknown')
    confidence = alert.get('explanation', 'No explanation')
    print(f"[{verdict}] {alert_type}")
    print(f"        {confidence}\n")
