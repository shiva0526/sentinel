#!/usr/bin/env python
"""Test Gemini API directly"""

import os
import google.generativeai as genai

# Load env
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key configured: {bool(api_key and api_key != 'user_will_fill_this')}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...\n")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    print("Testing Gemini API...")
    response = model.generate_content("Write a one-sentence security tip for website owners.")
    print(f"Response: {response.text}\n")
    print("SUCCESS: Gemini API is working!")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
