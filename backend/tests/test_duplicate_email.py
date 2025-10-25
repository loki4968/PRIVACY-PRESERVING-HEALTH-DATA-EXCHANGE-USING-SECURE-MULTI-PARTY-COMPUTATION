#!/usr/bin/env python3
"""
Test script to verify the "Email already registered" error handling
"""

import requests
import json

def test_duplicate_email():
    """Test registration with an email that's already registered"""
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 Testing Duplicate Email Registration")
    print("=" * 60)
    
    # Use a known registered email
    test_email = "test-new-911397@hospital.com"  # Use the email from the previous successful test
    
    test_user = {
        "name": "Duplicate Test Hospital",
        "email": test_email,
        "contact": "+1-555-0123",
        "type": "HOSPITAL",
        "location": "New York, NY",
        "password": "test123",
        "privacy_accepted": True
    }
    
    print(f"📧 Using already registered email: {test_email}")
    
    # Attempt to register with duplicate email
    print("\n📝 Attempting registration with duplicate email...")
    try:
        form_data = {
            'name': test_user['name'],
            'email': test_user['email'],
            'contact': test_user['contact'],
            'type': test_user['type'],
            'location': test_user['location'],
            'password': test_user['password'],
            'privacy_accepted': str(test_user['privacy_accepted']).lower()
        }
        
        response = requests.post(f"{base_url}/register", data=form_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400 and "Email already registered" in response.text:
            print("✅ Test passed: Received 'Email already registered' error as expected")
        else:
            print("❌ Test failed: Did not receive expected 'Email already registered' error")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Duplicate email test completed!")

if __name__ == "__main__":
    test_duplicate_email()