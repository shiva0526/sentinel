#!/usr/bin/env python
"""Debug attack agent"""

from agents.attack_agent import run_attack_agent

url = "https://www.akashbhumi.com/"
print(f"Testing attack agent on: {url}\n")

alerts = run_attack_agent(url)
print(f"\nAttack Agent Results:")
print(f"Total findings: {len(alerts)}")

for alert in alerts:
    print(f"\n- {alert.get('type')}: {alert.get('description')}")
    print(f"  Severity: {alert.get('raw_severity')}")
    print(f"  IP: {alert.get('ip')}")

if not alerts:
    print("No findings detected")
