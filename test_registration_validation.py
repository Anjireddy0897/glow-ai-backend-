import requests

url = "http://127.0.0.1:5000/api/register/"

def test_registration(description, data):
    print(f"Testing: {description}")
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)

# 1. Missing fields
test_registration("Missing all fields", {})

# 2. Email only
test_registration("Email only", {"email": "test@example.com"})

# 3. Password mismatch
test_registration("Password mismatch", {
    "email": "test@example.com",
    "full_name": "Test User",
    "age": "25",
    "gender": "Male",
    "password": "Password123!",
    "confirm_password": "WrongPassword"
})

# 4. Weak password (no uppercase)
test_registration("Weak password (no uppercase)", {
    "email": "test@example.com",
    "full_name": "Test User",
    "age": "25",
    "gender": "Male",
    "password": "password123!",
    "confirm_password": "password123!"
})

# 5. Strong password (should pass validation and hit DB check)
test_registration("Strong password", {
    "email": "test@example.com",
    "full_name": "Test User",
    "age": "25",
    "gender": "Male",
    "password": "StrongPassword123!",
    "confirm_password": "StrongPassword123!"
})
