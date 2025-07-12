import requests
import json

# Test the API endpoints
BASE_URL = "http://localhost:5000"

def test_ops_login():
    """Test ops login"""
    print("Testing Ops Login...")
    data = {
        "email": "ops@example.com",
        "password": "ops123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/ops/login", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json().get('access_token') if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_file_upload(token):
    """Test file upload"""
    print("\nTesting File Upload...")
    
    # Create a test file
    test_content = "This is a test document for upload testing."
    with open("test_upload.docx", "w") as f:
        f.write(test_content)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        with open("test_upload.docx", "rb") as f:
            files = {'file': ('test_upload.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(f"{BASE_URL}/api/ops/upload", files=files, headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Clean up
        import os
        if os.path.exists("test_upload.docx"):
            os.remove("test_upload.docx")
            
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing File Upload Issue...\n")
    
    # Test health first
    if not test_health():
        print("❌ Server not responding")
        exit(1)
    
    # Test login
    token = test_ops_login()
    if not token:
        print("❌ Login failed")
        exit(1)
    
    # Test upload
    if test_file_upload(token):
        print("✅ File upload working correctly")
    else:
        print("❌ File upload failed")
