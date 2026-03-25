"""FastAPI server for SentinelAI."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from agents.attack_agent import run_attack_agent
from agents.ingestion_agent import run_ingestion_agent
from agents.investigation_agent import run_investigation_agent
from agents.correlation_agent import run_correlation_agent
from agents.report_agent import run_report_agent
from agents.remediation_agent import run_remediation_agent

load_dotenv()
app = FastAPI(title="SentinelAI API", description="AI Security Alert Assistant")

# Add CORS to allow requests from our local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str

@app.post("/scan")
def scan_endpoint(request: ScanRequest):
    try:
        url = request.url
        if not url:
            url = "http://testphp.vulnweb.com"
            
        # Agent 1
        try:
            attack_alerts = run_attack_agent(url)
        except Exception as e:
            print(f"Attack Agent Error: {e}")
            attack_alerts = []
            
        # Agent 2
        try:
            unprocessed = run_ingestion_agent(attack_alerts)
        except Exception as e:
            print(f"Ingestion Agent Error: {e}")
            unprocessed = attack_alerts
            
        # Agent 3
        try:
            investigated = run_investigation_agent(unprocessed)
        except Exception as e:
            print(f"Investigation Agent Error: {e}")
            investigated = unprocessed
            
        # Agent 4
        try:
            incidents = run_correlation_agent(investigated)
        except Exception as e:
            print(f"Correlation Agent Error: {e}")
            incidents = []
            
        # Agent 5
        try:
            report_text = run_report_agent(investigated, incidents)
        except Exception as e:
            print(f"Report Agent Error: {e}")
            report_text = f"Failed to generate report: {e}"
            
        # Agent 6
        try:
            run_remediation_agent(investigated)
        except Exception as e:
            print(f"Remediation Agent Error: {e}")
            
        # Metrics
        total = len(investigated)
        critical = sum(1 for a in investigated if a.get('verdict') == 'CRITICAL')
        suspicious = sum(1 for a in investigated if a.get('verdict') == 'SUSPICIOUS')
        false_positives = sum(1 for a in investigated if a.get('verdict') == 'FALSE_POSITIVE')
        
        return {
            "total_alerts": total,
            "critical": critical,
            "suspicious": suspicious,
            "false_positives": false_positives,
            "report": report_text,
            "alerts": investigated
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report")
def get_report():
    try:
        path = os.path.join("db", "report.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return {"report": f.read()}
        return {"report": "No report found. Please run a scan first."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
