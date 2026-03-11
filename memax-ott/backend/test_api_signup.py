import requests
import json

def test_signup_api():
    base_url = "http://localhost:8000/api/auth/signup"
    
    # 1. Test Success (New User)
    import uuid
    uid = str(uuid.uuid4())[:8]
    unique_user = {
        "email": f"api_test_{uid}@example.com",
        "username": f"api_test_{uid}",
        "password": "password123",
        "full_name": "API Test User"
    }
    
    print(f"Testing signup with unique user: {unique_user['username']}")
    try:
        response = requests.post(base_url, json=unique_user)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Signup success!")
        else:
            print("❌ Signup failed!")
    except Exception as e:
        print(f"❌ Request failed: {e}")
        
    print("-" * 40)
    
    # 2. Test Duplicate User (Should fail with 400 now)
    print(f"Testing duplicate signup with same user: {unique_user['username']}")
    try:
        response = requests.post(base_url, json=unique_user)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("✅ Duplicate correctly handled (400 Bad Request)")
        elif response.status_code == 500:
            print("❌ Still getting 500 Internal Server Error!")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_signup_api()
