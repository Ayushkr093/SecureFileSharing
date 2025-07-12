"""
Simple Client Download Test - API Only
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_simple_client_workflow():
    """Test client workflow without database manipulation"""
    print("🚀 Testing Client Download Workflow via API")
    print("=" * 50)
    
    # Step 1: Create client via API
    print("\n📝 Step 1: Client Signup")
    signup_data = {
        "email": "apiclient@example.com",
        "password": "apipass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/client/signup", json=signup_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Signup failed: {e}")
        return
    
    # Step 2: Try login (will fail - needs verification)
    print("\n🔐 Step 2: Client Login (should fail - not verified)")
    login_data = {
        "email": "apiclient@example.com",
        "password": "apipass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/client/login", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected unverified user")
        
    except Exception as e:
        print(f"❌ Login test failed: {e}")
    
    # Step 3: Test ops login and file upload
    print("\n🔧 Step 3: Ops Login and Upload")
    ops_data = {
        "email": "ops@example.com",
        "password": "ops123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/ops/login", json=ops_data)
        if response.status_code == 200:
            ops_token = response.json().get('access_token')
            print(f"✅ Ops login successful")
            
            # Upload a test file
            test_content = "Test file for download testing"
            with open("download_test.docx", "w") as f:
                f.write(test_content)
            
            headers = {'Authorization': f'Bearer {ops_token}'}
            with open("download_test.docx", "rb") as f:
                files = {'file': ('download_test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                upload_response = requests.post(f"{BASE_URL}/api/ops/upload", files=files, headers=headers)
            
            print(f"Upload Status: {upload_response.status_code}")
            if upload_response.status_code == 201:
                file_info = upload_response.json()
                print(f"✅ File uploaded: {file_info}")
                
                # Clean up test file
                import os
                if os.path.exists("download_test.docx"):
                    os.remove("download_test.docx")
                
                return file_info.get('file_id')
            
    except Exception as e:
        print(f"❌ Ops workflow failed: {e}")
    
    return None

def test_with_manual_verification():
    """Test the download workflow with manual client verification"""
    print("\n🛠️ Step 4: Manual Client Verification")
    
    # Use the verification script
    try:
        import subprocess
        result = subprocess.run([
            'C:/Users/ayush/OneDrive/Desktop/Divansh/.venv/Scripts/python.exe',
            'verify_client.py'
        ], input='apiclient@example.com\n', text=True, capture_output=True)
        
        print(f"Verification output: {result.stdout}")
        if result.stderr:
            print(f"Verification errors: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Manual verification failed: {e}")
        return False
    
    # Now try client login again
    print("\n🔐 Step 5: Client Login (after verification)")
    login_data = {
        "email": "apiclient@example.com",
        "password": "apipass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/client/login", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            return response.json().get('access_token')
    except Exception as e:
        print(f"❌ Client login failed: {e}")
    
    return None

def test_client_download_features(client_token, file_id):
    """Test client download features"""
    if not client_token or not file_id:
        print("❌ Missing client token or file ID")
        return
    
    headers = {'Authorization': f'Bearer {client_token}'}
    
    # Test list files
    print("\n📋 Step 6: List Files")
    try:
        response = requests.get(f"{BASE_URL}/api/client/files", headers=headers)
        print(f"Status: {response.status_code}")
        files_data = response.json()
        print(f"Files: {files_data}")
        
        if response.status_code == 200:
            files = files_data.get('files', [])
            print(f"✅ Found {len(files)} files")
    except Exception as e:
        print(f"❌ List files failed: {e}")
    
    # Test get download link
    print(f"\n🔗 Step 7: Get Download Link for file {file_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/client/download-file/{file_id}", headers=headers)
        print(f"Status: {response.status_code}")
        download_data = response.json()
        print(f"Download data: {download_data}")
        
        if response.status_code == 200:
            download_link = download_data.get('download-link')
            print(f"✅ Download link: {download_link}")
            
            # Test actual download
            print("\n⬇️ Step 8: Download File")
            download_response = requests.get(download_link)
            print(f"Download Status: {download_response.status_code}")
            
            if download_response.status_code == 200:
                print(f"✅ File downloaded successfully! Size: {len(download_response.content)} bytes")
                
                # Test second download (should fail - single use)
                print("\n🚫 Step 9: Test Single-use Token")
                second_download = requests.get(download_link)
                print(f"Second download status: {second_download.status_code}")
                if second_download.status_code == 401:
                    print("✅ Single-use token working correctly")
                else:
                    print(f"⚠️ Token reuse issue: {second_download.json()}")
            else:
                print(f"❌ Download failed: {download_response.text}")
    except Exception as e:
        print(f"❌ Download workflow failed: {e}")

def main():
    # First test basic workflow
    file_id = test_simple_client_workflow()
    
    if file_id:
        # Then test with verification and downloads
        client_token = test_with_manual_verification()
        
        if client_token:
            test_client_download_features(client_token, file_id)
        else:
            print("❌ Could not get client token")
    else:
        print("❌ Could not upload test file")

if __name__ == "__main__":
    main()
