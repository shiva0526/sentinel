#!/usr/bin/env python
"""Test API with akashbhumi.com URL"""

import json
import urllib.request
import urllib.error

url = "https://www.akashbhumi.com/"

try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/scan",
        data=json.dumps({"url": url}).encode(),
        headers={"Content-Type": "application/json"}
    )
    print(f"Sending request to API with URL: {url}")
    resp = urllib.request.urlopen(req, timeout=180)
    data = json.loads(resp.read().decode())
    
    print(f"\nAPI Response Status: {resp.getcode()}")
    print(f"Total alerts: {data['total_alerts']}")
    print(f"Critical: {data['critical']}")
    print(f"Suspicious: {data['suspicious']}")
    print(f"False positives: {data['false_positives']}")
    
    if data['alerts']:
        print(f"\nFirst alert: {data['alerts'][0]}")
except urllib.error.URLError as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
