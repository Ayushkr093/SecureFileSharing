import requests
import json
import time

class APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.ops_token = None
        self.client_token = None
        self.test_results = {}
        
    def test_endpoint(self, name, method, path, headers=None, data=None, files=None, expected_status=None):
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        print(f"\n🧪 Testing {name}")
        print(f"   {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if files:
                    response = requests.post(url, headers=headers, files=files)
                else:
                    response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
                
            print(f"   Status: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response: {response.text}")
                
            # Check if status matches expected
            if expected_status and response.status_code != expected_status:
                self.test_results[name] = f"❌ Expected {expected_status}, got {response.status_code}"
            else:
                self.test_results[name] = f"✅ Success ({response.status_code})"
                
            return response
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results[name] = f"❌ Error: {e}"
            return None
    
    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Starting comprehensive API testing...")
        
        # 1. Health Check
        self.test_endpoint("Health Check", "GET", "/health", expected_status=200)
        
        # 2. API Info
        self.test_endpoint("API Info", "GET", "/api", expected_status=200)
        
        # 3. Ops Login
        ops_response = self.test_endpoint(
            "Ops Login", 
            "POST", 
            "/api/auth/ops/login",
            data={"email": "ops@example.com", "password": "ops123"},
            expected_status=200
        )
        
        if ops_response and ops_response.status_code == 200:
            self.ops_token = ops_response.json().get('access_token')
            print(f"   🔑 Ops token: {self.ops_token[:50]}...")
        
        # 4. Client Signup
        test_email = f"test{int(time.time())}@example.com"
        signup_response = self.test_endpoint(
            "Client Signup",
            "POST",
            "/api/auth/client/signup",
            data={"email": test_email, "password": "testpass123"},
            expected_status=201
        )
        
        # 5. Client Login (should fail - not verified)
        self.test_endpoint(
            "Client Login (Unverified)",
            "POST",
            "/api/auth/client/login",
            data={"email": test_email, "password": "testpass123"},
            expected_status=401
        )
        
        # 6. File Upload (Ops)
        if self.ops_token:
            # Create a test file
            test_content = b"This is a test document for API testing."
            files = {'file': ('test_api.docx', test_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            headers = {'Authorization': f'Bearer {self.ops_token}'}
            
            upload_response = self.test_endpoint(
                "File Upload",
                "POST",
                "/api/ops/upload",
                headers=headers,
                files=files,
                expected_status=201
            )
        
        # 7. Client File List (should fail - no token)
        self.test_endpoint(
            "Client Files (No Auth)",
            "GET",
            "/api/client/files",
            expected_status=401
        )
        
        # 8. Client File List (should fail - wrong user type)
        if self.ops_token:
            headers = {'Authorization': f'Bearer {self.ops_token}'}
            self.test_endpoint(
                "Client Files (Wrong User Type)",
                "GET",
                "/api/client/files",
                headers=headers,
                expected_status=403
            )
        
        # 9. Invalid Endpoints
        self.test_endpoint("Invalid Endpoint", "GET", "/api/invalid", expected_status=404)
        
        # 10. Download without token
        self.test_endpoint("Download No Token", "GET", "/download-file/invalid", expected_status=400)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            print(f"{result:<40} {test_name}")
            if result.startswith("✅"):
                passed += 1
            else:
                failed += 1
        
        print("="*60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {passed + failed}")
        print("="*60)
        
        if failed == 0:
            print("🎉 All tests passed! Your API is working perfectly!")
        else:
            print("⚠️  Some tests failed. Check the details above.")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
