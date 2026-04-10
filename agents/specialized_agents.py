import os
import json
import datetime
import google.generativeai as genai

def run_code_review_agent(directory: str = "."):
    """Simulates a secure code review of the project itself."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Perform a high-level secure code review of a Python project. Focus on: OWASP Top 10, insecure library usage, and hardcoded secrets. Generate a concise 3-point summary of potential improvements."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "- Use environment variables instead of hardcoded strings.\n- Implement rate limiting on all API endpoints.\n- Sanitize all user inputs before database insertion."

def run_consulting_agent():
    """Provides strategic security advice based on logged incidents."""
    incidents_path = os.path.join("db", "incidents.json")
    incident_count = 0
    if os.path.exists(incidents_path):
        with open(incidents_path, "r") as f:
            incident_count = len(json.load(f))
            
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"The client has seen {incident_count} security incidents recently. Give 2 strategic recommendations for a business owner to improve their security posture (1 technical, 1 organizational)."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "- Technical: Implement Multi-Factor Authentication (MFA) across all employee accounts.\n- Organizational: Conduct quarterly security awareness training for all staff."

def run_training_agent():
    """Generates an educational snippet about a cybersecurity topic."""
    topics = ["SQL Injection", "Cross-Site Scripting (XSS)", "Model Context Protocol (MCP)", "Agentic SOC"]
    import random
    topic = random.choice(topics)
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Explain the concept of '{topic}' in 3 simple sentences for a security trainee."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return f"{topic} is a critical security concept. It involves understanding how attackers exploit system weaknesses. Continuous monitoring is the best defense."
