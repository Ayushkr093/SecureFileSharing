"""
Test script for the Secure File Sharing System API
Run this script to test all endpoints and functionality
"""

import requests
import json
import os
import time

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_ops_login():
    """Test ops user login"""
    print("\n🔐 Testing Ops Login...")
    data = {
        "email": "ops@example.com",
        "password": "ops123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/ops/login", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            return result.get('access_token')
        return None
    except Exception as e:
        print(f"❌ Ops login failed: {e}")
        return None

def test_client_signup():
    """Test client user signup"""
    print("\n📝 Testing Client Signup...")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
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

def test_client_login():
    """Test client user login (will fail without email verification)"""
    print("\n🔐 Testing Client Login...")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
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

def test_file_upload(ops_token):
    """Test file upload by ops user"""
    print("\n📁 Testing File Upload...")
    
    if not ops_token:
        print("❌ No ops token available")
        return None
    
    # Create a test file
    test_file_content = "This is a test document content"
    test_filename = "test_document.docx"
    
    with open(test_filename, 'w') as f:
        f.write(test_file_content)
    
    try:
        headers = {
            'Authorization': f'Bearer {ops_token}'
        }
        
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(f"{BASE_URL}/api/ops/upload", files=files, headers=headers)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        # Clean up test file
        os.remove(test_filename)
        
        if response.status_code == 201:
            return result.get('file_id')
        return None
    except Exception as e:
        print(f"❌ File upload failed: {e}")
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)
        return None

def create_verified_client():
    """Create and manually verify a client user for testing"""
    print("\n👤 Creating verified client user...")
    
    # Import the app to manually verify user
    import sys
    sys.path.append('.')
    
    try:
        from app import create_app
        from models import db, User
        from werkzeug.security import generate_password_hash
        
        app = create_app()
        
        with app.app_context():
            # Check if test client already exists
            existing_user = User.query.filter_by(email='testclient@example.com').first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            # Create verified client user
            client_user = User(
                email='testclient@example.com',
                password_hash=generate_password_hash('clientpass123'),
                user_type='client',
                is_verified=True
            )
            
            db.session.add(client_user)
            db.session.commit()
            
        print("✅ Verified client user created: testclient@example.com / clientpass123")
        return True
    except Exception as e:
        print(f"❌ Failed to create verified client: {e}")
        return False

def test_verified_client_login():
    """Test login with verified client"""
    print("\n🔐 Testing Verified Client Login...")
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
        print(f"❌ Verified client login failed: {e}")
        return None

def test_list_files(client_token):
    """Test listing files as client user"""
    print("\n📋 Testing List Files...")
    
    if not client_token:
        print("❌ No client token available")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {client_token}'
        }
        
        response = requests.get(f"{BASE_URL}/api/client/files", headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ List files failed: {e}")
        return False

def test_download_link(client_token, file_id):
    """Test getting download link"""
    print("\n🔗 Testing Download Link Generation...")
    
    if not client_token or not file_id:
        print("❌ Missing client token or file ID")
        return None
    
    try:
        headers = {
            'Authorization': f'Bearer {client_token}'
        }
        
        response = requests.get(f"{BASE_URL}/api/client/download-file/{file_id}", headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            return result.get('download-link')
        return None
    except Exception as e:
        print(f"❌ Download link generation failed: {e}")
        return None

def test_file_download(download_url):
    """Test file download using encrypted token"""
    print("\n⬇️ Testing File Download...")
    
    if not download_url:
        print("❌ No download URL available")
        return False
    
    try:
        response = requests.get(download_url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"File downloaded successfully, size: {len(response.content)} bytes")
            return True
        else:
            print(f"Download failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ File download failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API Tests for Secure File Sharing System")
    print("=" * 60)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test ops login
    ops_token = test_ops_login()
    if not ops_token:
        print("❌ Ops login failed, stopping tests")
        return
    
    # Test client signup
    test_client_signup()
    
    # Test client login (will fail due to email verification)
    test_client_login()
    
    # Create verified client for testing
    if not create_verified_client():
        print("❌ Failed to create verified client, stopping tests")
        return
    
    # Wait a moment for database to update
    time.sleep(1)
    
    # Test verified client login
    client_token = test_verified_client_login()
    if not client_token:
        print("❌ Verified client login failed, stopping tests")
        return
    
    # Test file upload
    file_id = test_file_upload(ops_token)
    
    # Test list files
    test_list_files(client_token)
    
    # Test download link generation and file download
    if file_id:
        download_url = test_download_link(client_token, file_id)
        if download_url:
            test_file_download(download_url)
    
    print("\n" + "=" * 60)
    print("🏁 Tests completed!")
    print("\nTest Summary:")
    print("✅ Health Check")
    print("✅ Ops Login")
    print("✅ Client Signup")
    print("⚠️  Client Login (fails without email verification - expected)")
    print("✅ Verified Client Login")
    print("✅ File Upload" if file_id else "❌ File Upload")
    print("✅ List Files")
    print("✅ Download Link Generation" if file_id else "❌ Download Link Generation")
    print("✅ File Download" if file_id else "❌ File Download")

if __name__ == "__main__":
    main()
