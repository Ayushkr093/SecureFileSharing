import requests

try:
    print("Testing basic connectivity...")
    response = requests.get("http://localhost:5000/health")
    print(f"Health check status: {response.status_code}")
    print(f"Health check response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
