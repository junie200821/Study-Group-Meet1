import requests
import sys
import json
from datetime import datetime, timezone
import uuid

class StudyGroupAPITester:
    def __init__(self, base_url="https://studymeet.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user = f"test_user_{datetime.now().strftime('%H%M%S')}"
        self.created_session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - {name}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - {name}")
                print(f"   Expected status: {expected_status}, got: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - {name}")
            print(f"   Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )

    def test_user_login(self):
        """Test user login endpoint"""
        return self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data={"username": self.test_user}
        )

    def test_create_session(self):
        """Test session creation"""
        session_data = {
            "title": f"Test Session {datetime.now().strftime('%H:%M:%S')}",
            "description": "This is a test session for API testing",
            "date_time": (datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')),
            "tags": ["test", "api", "backend"]
        }
        
        success, response = self.run_test(
            "Create Session",
            "POST",
            "api/sessions",
            200,
            data=session_data
        )
        
        if success and 'session' in response:
            self.created_session_id = response['session']['id']
            print(f"   Created session ID: {self.created_session_id}")
        
        return success, response

    def test_get_all_sessions(self):
        """Test getting all sessions"""
        return self.run_test(
            "Get All Sessions",
            "GET",
            "api/sessions",
            200
        )

    def test_join_session(self):
        """Test joining a session"""
        if not self.created_session_id:
            print("❌ SKIPPED - Join Session (no session ID available)")
            return False, {}
            
        return self.run_test(
            "Join Session",
            "POST",
            f"api/sessions/{self.created_session_id}/join",
            200,
            params={"username": self.test_user}
        )

    def test_leave_session(self):
        """Test leaving a session"""
        if not self.created_session_id:
            print("❌ SKIPPED - Leave Session (no session ID available)")
            return False, {}
            
        return self.run_test(
            "Leave Session",
            "POST",
            f"api/sessions/{self.created_session_id}/leave",
            200,
            params={"username": self.test_user}
        )

    def test_trending_sessions(self):
        """Test getting trending sessions"""
        return self.run_test(
            "Get Trending Sessions",
            "GET",
            "api/sessions/trending",
            200
        )

    def test_invalid_session_join(self):
        """Test joining a non-existent session"""
        fake_session_id = str(uuid.uuid4())
        return self.run_test(
            "Join Invalid Session",
            "POST",
            f"api/sessions/{fake_session_id}/join",
            404,
            params={"username": self.test_user}
        )

    def test_invalid_session_leave(self):
        """Test leaving a non-existent session"""
        fake_session_id = str(uuid.uuid4())
        return self.run_test(
            "Leave Invalid Session",
            "POST",
            f"api/sessions/{fake_session_id}/leave",
            404,
            params={"username": self.test_user}
        )

def main():
    print("🚀 Starting Study Group Sessions API Tests")
    print("=" * 60)
    
    tester = StudyGroupAPITester()
    
    # Run all tests in sequence
    test_results = []
    
    # Basic functionality tests
    test_results.append(tester.test_health_endpoint())
    test_results.append(tester.test_user_login())
    test_results.append(tester.test_create_session())
    test_results.append(tester.test_get_all_sessions())
    test_results.append(tester.test_trending_sessions())
    
    # Session interaction tests
    test_results.append(tester.test_join_session())
    test_results.append(tester.test_leave_session())
    
    # Error handling tests
    test_results.append(tester.test_invalid_session_join())
    test_results.append(tester.test_invalid_session_leave())
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())