import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_reg(description, data):
    print(f"Testing: {description}")
    try:
        response = requests.post(f"{BASE_URL}/api/register/", json=data)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test 1: Simple password (6 chars)
test_reg("Simple 6-char password", {
    "email": "simple@example.com",
    "password": "123456",
    "confirm_password": "123456",
    "full_name": "Simple User",
    "age": 30,
    "gender": "Female"
})

# Test 2: Using 'fullname' alias
test_reg("Using 'fullname' alias", {
    "email": "alias@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "fullname": "Alias User",
    "age": "25",
    "gender": "Male"
})

# Test 3: Missing confirm password (should fail)
test_reg("Missing confirm_password", {
    "email": "missing@example.com",
    "password": "password123",
    "fullname": "No Confirm",
    "age": "25",
    "gender": "Male"
})
