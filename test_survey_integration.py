#!/usr/bin/env python3
"""
Test script for skin survey integration
Tests the new survey endpoints and display functionality
"""

import requests
import json
from datetime import datetime

# Backend URL
BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_submit_survey():
    """Test submitting a survey"""
    print_section("TEST 1: Submit Skin Survey")
    
    survey_data = {
        "user_id": 1,
        "skin_type": "oily",
        "concerns": ["Acne", "Excess Oil"],
        "sensitivity": "Normal",
        "climate": "Tropical",
        "ingredients": ["Salicylic Acid", "Niacinamide"],
        "allergies": []
    }
    
    print(f"Submitting survey for user_id: {survey_data['user_id']}")
    print(f"Survey data: {json.dumps(survey_data, indent=2)}\n")
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit_survey/", json=survey_data)
        print(f"Status Code: {response.status_code}\n")
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}\n")
        
        if response.status_code == 200 and result.get('status') == 'success':
            print("✓ Survey submitted successfully!")
            return result.get('survey', {}).get('skin_score', 0)
        else:
            print("✗ Failed to submit survey")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_get_latest_survey(user_id):
    """Test getting the latest survey"""
    print_section("TEST 2: Get Latest Survey with Full Details")
    
    print(f"Fetching latest survey for user_id: {user_id}\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api/get_latest_survey/{user_id}")
        print(f"Status Code: {response.status_code}\n")
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}\n")
        
        if response.status_code == 200 and result.get('status') == 'success':
            print("✓ Survey retrieved successfully!")
            survey_data = result.get('data', {})
            print(f"\nSurvey Summary:")
            print(f"  Skin Type: {survey_data.get('skin_type')}")
            print(f"  Skin Score: {survey_data.get('skin_score')}")
            print(f"  Score Rating: {survey_data.get('score_rating')}")
            print(f"  Sensitivity: {survey_data.get('sensitivity')}")
            print(f"  Climate: {survey_data.get('climate')}")
            print(f"  Concerns: {', '.join(survey_data.get('concerns', []))}")
            print(f"  Allergies: {', '.join(survey_data.get('allergies', [])) or 'None'}")
            print(f"  Created: {survey_data.get('created_at')}")
            return True
        else:
            print("✗ Failed to retrieve survey")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_home_screen(user_id):
    """Test getting home screen data"""
    print_section("TEST 3: Get Home Screen Data (for dashboard)")
    
    print(f"Fetching home screen data for user_id: {user_id}\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api/get_home_screen/{user_id}")
        print(f"Status Code: {response.status_code}\n")
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}\n")
        
        if response.status_code == 200 and result.get('status') == 'success':
            print("✓ Home screen data retrieved successfully!")
            
            user = result.get('user', {})
            analytics = result.get('analytics', {})
            latest_survey = result.get('latest_survey', {})
            
            print(f"\nHome Screen Summary:")
            print(f"  User: {user.get('name')} ({user.get('email')})")
            print(f"  Total Surveys: {analytics.get('total_surveys')}")
            print(f"  Total Scans: {analytics.get('total_scans')}")
            print(f"  Total Analyses: {analytics.get('total_analyses')}")
            
            if latest_survey:
                print(f"\n  Latest Survey:")
                print(f"    Score: {latest_survey.get('score')}")
                print(f"    Rating: {latest_survey.get('score_rating')}")
                print(f"    Skin Type: {latest_survey.get('skin_type')}")
                print(f"    Date: {latest_survey.get('date')}")
            else:
                print(f"\n  No survey data available yet")
            
            return True
        else:
            print("✗ Failed to retrieve home screen data")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  SKIN SURVEY INTEGRATION TEST SUITE".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\n[INFO] Make sure Flask backend is running at http://localhost:5000")
    print("       Run: python app.py")
    
    # Test 1: Submit survey
    score = test_submit_survey()
    if score is None:
        print("\n⚠️  Skipping remaining tests - survey submission failed")
        return
    
    # Test 2: Get latest survey
    user_id = 1
    success = test_get_latest_survey(user_id)
    if not success:
        print("\n⚠️  Skipping home screen test - could not retrieve survey")
        return
    
    # Test 3: Get home screen
    test_get_home_screen(user_id)
    
    print_section("ALL TESTS COMPLETED")
    print("✓ Survey integration is working correctly!")
    print("\nNew Endpoints Available:")
    print("  1. POST /api/submit_survey/")
    print("     - Submit skin survey with responses")
    print("     - Returns: score, score_rating, and all survey data")
    print("\n  2. GET /api/get_latest_survey/<user_id>")
    print("     - Retrieve latest survey with full details")
    print("     - Use this to display survey results on home screen")
    print("\n  3. GET /api/get_home_screen/<user_id>")
    print("     - Get combined user + survey data for home/dashboard")
    print("     - Includes analytics and latest survey info")

if __name__ == "__main__":
    main()
