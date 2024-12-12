import requests
import json
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def test_create_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Test user creation endpoint."""
        print("\nTesting user creation...")
        response = requests.post(
            f"{self.base_url}/users/",
            json={
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    
    def test_login(self, email: str, password: str) -> None:
        """Test login endpoint and get access token."""
        print("\nTesting login...")
        response = requests.post(
            f"{self.base_url}/token",
            data={
                "username": email,
                "password": password
            }
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print("Token received")
        self.token = result["access_token"]
    
    def test_recommendations(self, limit: int = 5) -> Dict[str, Any]:
        """Test recommendations endpoint."""
        print("\nTesting recommendations...")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/recommendations/",
            headers=headers,
            params={"limit": limit}
        )
        print(f"Status: {response.status_code}")
        print(f"Recommendations: {json.dumps(response.json(), indent=2)}")
        return response.json()
    
    def test_submit_rating(self, content_id: str, rating: float) -> Dict[str, Any]:
        """Test rating submission endpoint."""
        print("\nTesting rating submission...")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/ratings/",
            headers=headers,
            json={
                "content_id": content_id,
                "rating": rating
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    
    def test_get_content(self, limit: int = 5) -> Dict[str, Any]:
        """Test content listing endpoint."""
        print("\nTesting content listing...")
        response = requests.get(
            f"{self.base_url}/content/",
            params={"limit": limit}
        )
        print(f"Status: {response.status_code}")
        print(f"Content: {json.dumps(response.json(), indent=2)}")
        return response.json()

def run_tests():
    """Run all API tests."""
    tester = APITester()
    
    # Test user creation and login
    test_email = "test@example.com"
    test_password = "testpassword123"
    test_name = "Test User"
    
    tester.test_create_user(test_email, test_password, test_name)
    tester.test_login(test_email, test_password)
    
    # Test content endpoints
    content = tester.test_get_content()
    if content:
        # Test rating submission for first content item
        first_content = content[0]
        tester.test_submit_rating(first_content["content_id"], 4.5)
    
    # Test recommendations
    tester.test_recommendations()

if __name__ == "__main__":
    run_tests()
