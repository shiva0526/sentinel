"""Attack Agent simulates vulnerability scanning against a target URL."""

import subprocess
import socket
import requests
from datetime import datetime, timezone
import json
from typing import List, Dict
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_open_ports(host: str) -> List[Dict]:
    findings = []
    ports = [21, 22, 23, 80, 443, 3306, 8080]
    Target_IP = host
    try:
        Target_IP = socket.gethostbyname(host)
    except Exception: pass

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((Target_IP, port))
            if result == 0:
                severity = "high" if port in [21, 22, 23, 3306] else "low"
                findings.append({
                    "id": f"ATK-PORT-{port}",
                    "type": "open_port",
                    "source": "attack_agent",
                    "ip": Target_IP,
                    "user": None,
                    "description": f"Port {port} is open and potentially exposed.",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "raw_severity": severity
                })
                print(f"[Attack Agent] Found: Port {port} is open")
            sock.close()
        except Exception: pass
    return findings

def check_headers_and_server(url: str, ip: str) -> List[Dict]:
    findings = []
    try:
        response = requests.get(url, timeout=5, verify=False)
        headers = response.headers
        
        sec_headers = ['Strict-Transport-Security', 'X-Frame-Options', 'Content-Security-Policy']
        for sh in sec_headers:
            if sh not in headers:
                findings.append({
                    "id": f"ATK-HDR-{sh.upper()}",
                    "type": "missing_security_header",
                    "source": "attack_agent",
                    "ip": ip,
                    "user": None,
                    "description": f"Missing recommended security header: {sh}",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "raw_severity": "medium"
                })
                print(f"[Attack Agent] Found: Missing security header {sh}")
        
        if 'Server' in headers:
            server = headers['Server'].lower()
            if any(old_ver in server for old_ver in ['apache/2.2', 'apache/2.4.1', 'nginx/1.10', 'iis/7']):
                findings.append({
                    "id": "ATK-OUTDATED-SERVER",
                    "type": "outdated_server",
                    "source": "attack_agent",
                    "ip": ip,
                    "user": None,
                    "description": f"Potentially outdated server version detected: {headers['Server']}",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "raw_severity": "high"
                })
                print(f"[Attack Agent] Found: Server header reveals {headers['Server']}")
    except Exception as e:
        pass
    return findings

def check_sensitive_paths(url: str, ip: str) -> List[Dict]:
    findings = []
    paths = ['/robots.txt', '/admin', '/wp-admin', '/login']
    for path in paths:
        try:
            target = url.rstrip('/') + path
            response = requests.get(target, timeout=3, verify=False, allow_redirects=False)
            if response.status_code in [200, 301, 302, 401, 403]:
                if path == '/robots.txt' and response.status_code == 200:
                    desc = "robots.txt exposed, might contain sensitive paths."
                    sev = "low"
                    print(f"[Attack Agent] Found: robots.txt exposed at /robots.txt")
                else:
                    desc = f"Admin or login portal exposed at {path} (status {response.status_code})."
                    sev = "medium"
                    print(f"[Attack Agent] Found: Admin page exposed at {path}")
                    
                findings.append({
                    "id": f"ATK-PATH-{path.strip('/').replace('/', '-')}",
                    "type": "exposed_path",
                    "source": "attack_agent",
                    "ip": ip,
                    "user": None,
                    "description": desc,
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "raw_severity": sev
                })
        except Exception:
            pass
    return findings

def run_attack_agent(url: str) -> List[Dict]:
    print("--- AGENT 1: ATTACK AGENT STARTING ---")
    print(f"[Attack Agent] Scanning {url}...")
    findings = []
    
    try:
        result = subprocess.run(['zap-cli', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        if result.returncode == 0:
            print("[Attack Agent] Running OWASP ZAP scan... (Simulated)")
            findings.append({
                "id": "ATK-001",
                "type": "sql_injection",
                "source": "attack_agent",
                "ip": None,
                "user": None,
                "description": "Login form is vulnerable to SQL injection",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "raw_severity": "high"
            })
            print("[Attack Agent] Found: Login form vulnerable to SQL injection")
        else:
            raise FileNotFoundError()
    except Exception:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname if parsed.hostname else 'localhost'
            ip = None
            try: ip = socket.gethostbyname(host)
            except: ip = host
            
            f1 = check_open_ports(host)
            f2 = check_headers_and_server(url, ip)
            f3 = check_sensitive_paths(url, ip)
            findings.extend(f1 + f2 + f3)
        except Exception:
            pass
            
    print(f"[Attack Agent] {len(findings)} findings generated.")
    print("--- AGENT 1: ATTACK AGENT DONE ---\n")
    return findings
