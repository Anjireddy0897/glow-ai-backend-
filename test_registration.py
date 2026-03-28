#!/usr/bin/env python
"""
Test script to verify registration endpoint is working
"""
import requests
import json
import os
import sys

# Change to the facecream directory
os.chdir(r'c:\facecream')

BASE_URL = "http://localhost:5000"

def test_registration():
    """Test user registration"""
    print("\n" + "="*60)
    print("TESTING REGISTRATION ENDPOINT")
    print("="*60)
    
    # Test data
    test_user = {
        "email": "testuser123@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "full_name": "Test User",
        "age": "25",
        "gender": "Male"
    }
    
    print("\n[TEST] Sending registration request with:")
    print(f"  Email: {test_user['email']}")
    print(f"  Name: {test_user['full_name']}")
    print(f"  Age: {test_user['age']}")
    print(f"  Gender: {test_user['gender']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/register/",
            json=test_user,
            timeout=10
        )
        
        print(f"\n[RESPONSE] Status Code: {response.status_code}")
        print(f"[RESPONSE] Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"[RESPONSE] Body:")
            print(json.dumps(data, indent=2))
            
            if response.status_code in [200, 201]:
                print("\n✓ Registration successful!")
                if 'user_id' in data:
                    return data['user_id']
            else:
                print("\n✗ Registration failed!")
                
        except json.JSONDecodeError:
            print(f"[RESPONSE] Raw text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to Flask app!")
        print("  Make sure the app is running: python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        sys.exit(1)


def test_invalid_registration():
    """Test registration with missing fields"""
    print("\n" + "="*60)
    print("TESTING INVALID REGISTRATION (Missing Fields)")
    print("="*60)
    
    invalid_user = {
        "email": "invalid@example.com",
        # Missing password, confirm_password, full_name, age, gender
    }
    
    print("\n[TEST] Sending registration request with missing fields...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/register/",
            json=invalid_user,
            timeout=10
        )
        
        print(f"\n[RESPONSE] Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"[RESPONSE] Body:")
            print(json.dumps(data, indent=2))
            
            if response.status_code == 400:
                print("\n✓ Correctly rejected invalid registration!")
            
        except json.JSONDecodeError:
            print(f"[RESPONSE] Raw text: {response.text}")
            
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("\n[INFO] Make sure the Flask app is running!")
    print("[INFO] Start the app with: python app.py")
    
    test_registration()
    test_invalid_registration()
    
    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60 + "\n")
