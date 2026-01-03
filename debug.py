"""
Resume Parser DEBUG Script
Run this to see exactly what's breaking
"""

import json
import requests
from src.parser import ResumeParser
from src.config import settings
import traceback
import os
print("🧪 Starting Resume Parser Debug...")
print(f"Current dir: {os.getcwd()}")
print(f"API key loaded: {'✅' if settings.perplexity_api_key else '❌'}")

# Initialize parser
parser = ResumeParser(settings.perplexity_api_key)
print("✅ Parser initialized")

# Test 1: Simple text extraction
print("\n1️⃣ Testing text extraction...")
sample_text = """
Kunal Gaikwad
kunal@example.com | 8928008966 | Nashik, India

Senior ML Engineer
Tech Corp | 2023-Present
• Built RAG systems with FastAPI
• Deployed models to AWS

MSc Artificial Intelligence
Sheffield Hallam University | 2025
"""

print(f"Sample text length: {len(sample_text)}")
print("✅ Text extraction test passed")

# Test 2: Raw API call
print("\n2️⃣ Testing raw Perplexity API...")
try:
    prompt = "Return JSON: {\"test\": \"works\"}"
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {settings.perplexity_api_key}", "Content-Type": "application/json"},
        json={
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        },
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print("Raw response keys:", list(response.json().keys()))
    
    if response.status_code == 200:
        result = response.json()
        print("Choices length:", len(result.get('choices', [])))
        if result.get('choices'):
            print("Choice[0] keys:", list(result['choices'][0].keys()))
            print("Message keys:", list(result['choices'][0].get('message', {}).keys()))
            print("Raw content:", repr(result['choices'][0]['message']['content'][:200]))
    else:
        print("Error response:", response.text)
        
except Exception as e:
    print(f"API Error: {e}")

# Test 3: Full parse
print("\n3️⃣ Testing full parse...")
try:
    result = parser.parse_with_llm(sample_text)
    print("✅ Full parse SUCCESS!")
    print("Output:", json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Full parse FAILED!")
    print("Error:", str(e))
    print("Traceback:")
    traceback.print_exc()

print("\n🔍 Debug complete. Check outputs above.")
