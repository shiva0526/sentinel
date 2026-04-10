#!/usr/bin/env python
"""Test script to debug alert processing."""

from agents.ingestion_agent import run_ingestion_agent
from agents.investigation_agent import run_investigation_agent

print("=== Testing Alert Processing ===\n")

unprocessed = run_ingestion_agent([])
print(f"\nUnprocessed alerts: {len(unprocessed)}")
if unprocessed:
    print(f"First alert ID: {unprocessed[0].get('id')}")
    print(f"First alert type: {unprocessed[0].get('type')}")

investigated = run_investigation_agent(unprocessed)
print(f"\nInvestigated alerts: {len(investigated)}")
for alert in investigated:
    print(f"  - {alert.get('id')}: {alert.get('verdict')} ({alert.get('confidence')})")
