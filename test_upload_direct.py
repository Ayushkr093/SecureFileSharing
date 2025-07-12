import requests
import json

# Test the upload API directly
def test_upload():
    print("🧪 Testing file upload API directly...")
    
    # First, login to get a token
    login_url = "http://localhost:5000/api/auth/ops/login"
    login_data = {
        "email": "ops@example.com",
        "password": "ops123"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(login_url, json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print(f"✅ Got token: {token[:50]}...")
        
        # Now try to upload a file
        upload_url = "http://localhost:5000/api/ops/upload"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Create a simple test file
        test_content = "This is a test document."
        files = {
            'file': ('test.docx', test_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        print("📤 Uploading file...")
        upload_response = requests.post(upload_url, headers=headers, files=files)
        print(f"Upload status: {upload_response.status_code}")
        print(f"Upload response: {upload_response.text}")
        
        if upload_response.status_code == 201:
            print("✅ Upload successful!")
        else:
            print("❌ Upload failed!")
    else:
        print(f"❌ Login failed: {login_response.text}")

if __name__ == "__main__":
    test_upload()
