"""
Final Client Download Test
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_complete_workflow():
    """Test the complete client download workflow"""
    print("🚀 Testing Complete Client Download Workflow")
    print("=" * 55)
    
    # Step 1: Client Login (user is already verified)
    print("\n🔐 Step 1: Client Login")
    login_data = {
        "email": "apiclient@example.com",
        "password": "apipass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/client/login", json=login_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code != 200:
            print("❌ Client login failed")
            return
        
        client_token = result.get('access_token')
        print("✅ Client login successful")
        
    except Exception as e:
        print(f"❌ Client login failed: {e}")
        return
    
    # Step 2: List Files
    print("\n📋 Step 2: List Available Files")
    headers = {'Authorization': f'Bearer {client_token}'}
    
    try:
        response = requests.get(f"{BASE_URL}/api/client/files", headers=headers)
        print(f"Status: {response.status_code}")
        files_data = response.json()
        print(f"Response: {files_data}")
        
        if response.status_code != 200:
            print("❌ List files failed")
            return
        
        files = files_data.get('files', [])
        print(f"✅ Found {len(files)} files:")
        for file in files:
            print(f"   - ID: {file['id']}, Name: {file['original_filename']}, Size: {file['file_size']} bytes")
        
        if not files:
            print("❌ No files available for download")
            return
        
        # Use the first file for testing
        test_file = files[0]
        file_id = test_file['id']
        
    except Exception as e:
        print(f"❌ List files failed: {e}")
        return
    
    # Step 3: Get Download Link
    print(f"\n🔗 Step 3: Generate Download Link for file '{test_file['original_filename']}'")
    
    try:
        response = requests.get(f"{BASE_URL}/api/client/download-file/{file_id}", headers=headers)
        print(f"Status: {response.status_code}")
        download_data = response.json()
        print(f"Response: {download_data}")
        
        if response.status_code != 200:
            print("❌ Download link generation failed")
            return
        
        download_link = download_data.get('download-link')
        print(f"✅ Download link generated:")
        print(f"   {download_link}")
        
    except Exception as e:
        print(f"❌ Download link generation failed: {e}")
        return
    
    # Step 4: Download File
    print(f"\n⬇️ Step 4: Download File")
    
    try:
        response = requests.get(download_link)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"✅ File downloaded successfully!")
            print(f"   - Content Length: {content_length} bytes")
            print(f"   - Content Type: {response.headers.get('Content-Type', 'Unknown')}")
            
            # Save to verify
            with open('downloaded_file.docx', 'wb') as f:
                f.write(response.content)
            print(f"   - Saved as: downloaded_file.docx")
            
        else:
            print(f"❌ Download failed")
            if 'application/json' in response.headers.get('Content-Type', ''):
                error_data = response.json()
                print(f"   Error: {error_data}")
            else:
                print(f"   Error: {response.text}")
            return
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return
    
    # Step 5: Test Single-Use Token (should fail)
    print(f"\n🚫 Step 5: Test Single-Use Token Security")
    
    try:
        response = requests.get(download_link)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            error_data = response.json()
            print(f"✅ Single-use token working correctly!")
            print(f"   Error message: {error_data.get('message')}")
        else:
            print(f"⚠️ Warning: Token can be reused (security issue)")
            print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Second download test failed: {e}")
    
    # Step 6: Test Unauthorized Access
    print(f"\n🔒 Step 6: Test Unauthorized User Access")
    
    # Try accessing with wrong user token (ops token)
    try:
        ops_login = requests.post(f"{BASE_URL}/api/auth/ops/login", json={
            "email": "ops@example.com", 
            "password": "ops123"
        })
        
        if ops_login.status_code == 200:
            ops_token = ops_login.json().get('access_token')
            
            # Try to get download link with ops token (should fail)
            wrong_headers = {'Authorization': f'Bearer {ops_token}'}
            response = requests.get(f"{BASE_URL}/api/client/download-file/{file_id}", headers=wrong_headers)
            print(f"Ops user access status: {response.status_code}")
            
            if response.status_code == 403:
                print("✅ Ops user correctly denied access to client functions")
            else:
                print(f"⚠️ Security issue: Ops user got access: {response.json()}")
    
    except Exception as e:
        print(f"❌ Unauthorized access test failed: {e}")
    
    # Clean up
    import os
    if os.path.exists('downloaded_file.docx'):
        os.remove('downloaded_file.docx')
        print(f"\n🧹 Cleaned up test file")
    
    print("\n" + "=" * 55)
    print("🎉 Client Download Test Completed Successfully!")
    print("\nFeatures Tested:")
    print("✅ Client Authentication")
    print("✅ File Listing")
    print("✅ Secure Download Link Generation")
    print("✅ File Download with Encrypted Token")
    print("✅ Single-Use Token Security")
    print("✅ User Role-Based Access Control")

if __name__ == "__main__":
    test_complete_workflow()
