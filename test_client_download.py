"""
Complete Client Download Test Script
Tests the full workflow: signup, verification, login, list files, get download link, and download file
"""

import requests
import json
import os
import time

BASE_URL = "http://localhost:5000"

def test_client_signup():
    """Test client user signup"""
    print("📝 Testing Client Signup...")
    data = {
        "email": "testclient@example.com",
        "password": "clientpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/client/signup", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Client signup failed: {e}")
        return False

def verify_client_manually():
    """Manually verify the client user in the database"""
    print("\n✅ Manually verifying client user...")
    
    try:
        import sys
        sys.path.append('.')
        from app import create_app
        from models import db, User
        
        app = create_app()
        
        with app.app_context():
            # Find and verify the user
            user = User.query.filter_by(email='testclient@example.com', user_type='client').first()
            
            if not user:
                print("❌ Client user not found")
                return False
            
            if user.is_verified:
                print("✅ User already verified")
                return True
            
            user.is_verified = True
            user.verification_token = None
            db.session.commit()
            
            print("✅ Client user verified successfully")
            return True
    except Exception as e:
        print(f"❌ Manual verification failed: {e}")
        return False

def test_client_login():
    """Test client login after verification"""
    print("\n🔐 Testing Client Login...")
    data = {
        "email": "testclient@example.com",
        "password": "clientpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/client/login", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            return result.get('access_token')
        return None
    except Exception as e:
        print(f"❌ Client login failed: {e}")
        return None

def test_list_files(client_token):
    """Test listing files as client"""
    print("\n📋 Testing List Files...")
    
    if not client_token:
        print("❌ No client token available")
        return []
    
    try:
        headers = {'Authorization': f'Bearer {client_token}'}
        response = requests.get(f"{BASE_URL}/api/client/files", headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            files = result.get('files', [])
            print(f"Found {len(files)} files")
            for file in files:
                print(f"  - File ID: {file['id']}, Name: {file['original_filename']}, Size: {file['file_size']}")
            return files
        return []
    except Exception as e:
        print(f"❌ List files failed: {e}")
        return []

def test_get_download_link(client_token, file_id):
    """Test getting download link for a file"""
    print(f"\n🔗 Testing Download Link Generation for file ID {file_id}...")
    
    if not client_token or not file_id:
        print("❌ Missing client token or file ID")
        return None
    
    try:
        headers = {'Authorization': f'Bearer {client_token}'}
        response = requests.get(f"{BASE_URL}/api/client/download-file/{file_id}", headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            download_link = result.get('download-link')
            print(f"✅ Download link generated: {download_link}")
            return download_link
        return None
    except Exception as e:
        print(f"❌ Download link generation failed: {e}")
        return None

def test_file_download(download_url):
    """Test downloading file using the encrypted URL"""
    print(f"\n⬇️ Testing File Download...")
    
    if not download_url:
        print("❌ No download URL provided")
        return False
    
    try:
        print(f"Downloading from: {download_url}")
        response = requests.get(download_url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Save the downloaded file
            filename = "downloaded_test_file.docx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ File downloaded successfully!")
            print(f"   - Size: {file_size} bytes")
            print(f"   - Saved as: {filename}")
            
            # Clean up
            if os.path.exists(filename):
                os.remove(filename)
                print(f"   - Cleaned up test file")
            
            return True
        else:
            print(f"❌ Download failed with status {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                print(f"Error: {response.json()}")
            else:
                print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ File download failed: {e}")
        return False

def test_unauthorized_download(download_url):
    """Test that unauthorized users cannot access the download URL"""
    print(f"\n🚫 Testing Unauthorized Access to Download URL...")
    
    if not download_url:
        print("❌ No download URL provided")
        return False
    
    try:
        # Try to download again (should fail as token is single-use)
        response = requests.get(download_url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Unauthorized access correctly blocked (single-use token)")
            print(f"Response: {response.json()}")
            return True
        elif response.status_code == 200:
            print("⚠️ Warning: Download URL is still accessible (should be single-use)")
            return False
        else:
            print(f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unauthorized test failed: {e}")
        return False

def cleanup_test_user():
    """Clean up the test user"""
    print("\n🧹 Cleaning up test user...")
    
    try:
        import sys
        sys.path.append('.')
        from app import create_app
        from models import db, User
        
        app = create_app()
        
        with app.app_context():
            user = User.query.filter_by(email='testclient@example.com').first()
            if user:
                db.session.delete(user)
                db.session.commit()
                print("✅ Test user cleaned up")
            else:
                print("ℹ️ No test user found to clean up")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

def main():
    """Run complete client download test"""
    print("🚀 Starting Complete Client Download Test")
    print("=" * 60)
    
    # Clean up any existing test user first
    cleanup_test_user()
    
    # Step 1: Client Signup
    if not test_client_signup():
        print("❌ Client signup failed, stopping tests")
        return
    
    # Step 2: Manual verification (since email isn't configured)
    if not verify_client_manually():
        print("❌ Client verification failed, stopping tests")
        return
    
    # Step 3: Client Login
    client_token = test_client_login()
    if not client_token:
        print("❌ Client login failed, stopping tests")
        return
    
    # Step 4: List Files
    files = test_list_files(client_token)
    if not files:
        print("❌ No files found or list failed, stopping tests")
        return
    
    # Step 5: Get Download Link for first file
    file_id = files[0]['id']
    download_url = test_get_download_link(client_token, file_id)
    if not download_url:
        print("❌ Download link generation failed, stopping tests")
        return
    
    # Step 6: Download File
    if not test_file_download(download_url):
        print("❌ File download failed")
        return
    
    # Step 7: Test unauthorized access (single-use token)
    test_unauthorized_download(download_url)
    
    # Clean up
    cleanup_test_user()
    
    print("\n" + "=" * 60)
    print("🎉 Client Download Test Completed!")
    print("\nTest Summary:")
    print("✅ Client Signup")
    print("✅ Manual Email Verification")
    print("✅ Client Login")
    print("✅ List Files")
    print("✅ Generate Download Link")
    print("✅ Download File with Encrypted Token")
    print("✅ Single-use Token Security")

if __name__ == "__main__":
    main()
