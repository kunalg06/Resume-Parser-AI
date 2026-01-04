import requests
import json

API_URL = "http://127.0.0.1:8000"

# Test health
print("Testing health endpoint...")
response = requests.get(f"{API_URL}/health")
print(json.dumps(response.json(), indent=2))

# Test parse
print("\nTesting parse endpoint...")
with open("sample_resume.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_URL}/parse", files=files)
    print(json.dumps(response.json(), indent=2))
