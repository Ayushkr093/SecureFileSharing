"""
Test Frontend Upload Issue
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_ops_upload_api():
    """Test the ops upload API endpoint directly"""
    print("🔧 Testing Ops Upload API...")
    
    # Step 1: Login as ops user
    login_data = {
        "email": "ops@example.com",
        "password": "ops123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/ops/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.json()}")
            return
        
        ops_token = response.json().get('access_token')
        print("✅ Ops login successful")
        
        # Step 2: Test file upload
        print("\n📁 Testing File Upload...")
        
        # Create a test file
        test_content = "This is a test document for frontend upload testing"
        with open("frontend_test.docx", "w") as f:
            f.write(test_content)
        
        headers = {'Authorization': f'Bearer {ops_token}'}
        
        with open("frontend_test.docx", "rb") as f:
            files = {'file': ('frontend_test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            upload_response = requests.post(f"{BASE_URL}/api/ops/upload", files=files, headers=headers)
        
        print(f"Upload Status: {upload_response.status_code}")
        print(f"Upload Response: {upload_response.json()}")
        
        # Clean up
        import os
        if os.path.exists("frontend_test.docx"):
            os.remove("frontend_test.docx")
        
        if upload_response.status_code == 201:
            print("✅ File upload API working correctly")
            return True
        else:
            print("❌ File upload API failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_frontend_simulation():
    """Simulate frontend upload behavior"""
    print("\n🌐 Simulating Frontend Upload...")
    
    # Test the exact same request that frontend would make
    login_data = {
        "email": "ops@example.com",
        "password": "ops123"
    }
    
    # Get token
    response = requests.post(f"{BASE_URL}/api/auth/ops/login", json=login_data)
    if response.status_code != 200:
        print("❌ Cannot get token")
        return
    
    token = response.json().get('access_token')
    
    # Create test file
    test_content = b"Test file content for frontend simulation"
    
    # Simulate exact frontend request
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    files = {
        'file': ('test.docx', test_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ops/upload", files=files, headers=headers)
        print(f"Frontend simulation status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Frontend simulation successful")
        else:
            print("❌ Frontend simulation failed")
    except Exception as e:
        print(f"❌ Frontend simulation error: {e}")

def test_cors_headers():
    """Test CORS headers"""
    print("\n🔗 Testing CORS Headers...")
    
    try:
        # Test preflight request
        headers = {
            'Origin': 'http://localhost:5000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'authorization,content-type'
        }
        
        response = requests.options(f"{BASE_URL}/api/ops/upload", headers=headers)
        print(f"CORS preflight status: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"❌ CORS test error: {e}")

if __name__ == "__main__":
    print("🔍 Debugging Frontend Upload Issue")
    print("=" * 50)
    
    # Test API directly
    if test_ops_upload_api():
        # Test frontend simulation
        test_frontend_simulation()
        
        # Test CORS
        test_cors_headers()
    else:
        print("❌ API test failed, skipping other tests")
