import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_api(endpoint, description, data):
    print(f"\nTesting {endpoint}: {description}")
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        print(f"Status: {response.status_code}")
        body = response.json()
        print(f"Body keys: {list(body.keys())}")
        if "user" in body:
            print(f"User object keys: {list(body['user'].keys())}")
        else:
            print("ERROR: 'user' object missing!")
        
        # Check for both id and user_id
        if "id" in body and "user_id" in body:
            print("SUCCESS: Both 'id' and 'user_id' found at top level.")
        else:
            print("ERROR: 'id' or 'user_id' missing at top level!")
            
        return body
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test Registration
reg_data = {
    "email": "sync_test@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "full_name": "Sync Test User",
    "age": "25",
    "gender": "Other"
}
test_api("/api/register/", "Register with new format", reg_data)

# Test Login
login_data = {
    "email": "sync_test@example.com",
    "password": "password123"
}
test_api("/api/login/", "Login with new format", login_data)
