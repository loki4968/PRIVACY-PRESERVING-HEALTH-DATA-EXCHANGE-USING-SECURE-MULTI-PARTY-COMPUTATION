#!/usr/bin/env python3
"""
Test script to verify that unverified users cannot log in
"""

import requests
import random
import json
from models import SessionLocal, Organization

def test_unverified_login():
    """Test that unverified users cannot log in"""
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 Testing Unverified User Login Restriction")
    print("=" * 60)
    
    # Create a new user with email_verified=False
    random_id = random.randint(10000, 99999)
    test_email = f"test-unverified-{random_id}@hospital.com"
    
    test_user = {
        "name": "Unverified Test Hospital",
        "email": test_email,
        "contact": "+1-555-0123",
        "type": "HOSPITAL",
        "location": "New York, NY",
        "password": "test123",
        "privacy_accepted": True
    }
    
    print(f"📧 Using test email: {test_email}")
    
    # Step 1: Register organization
    print("\n📝 Step 1: Registering organization...")
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
        
        if response.status_code == 200:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            return
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Step 2: Verify the user is in the database with email_verified=False
    print("\n🔍 Step 2: Verifying user is in database with email_verified=False...")
    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.email == test_user['email']).first()
        if org:
            print(f"✅ User found in database")
            print(f"✅ Email verified status: {org.email_verified}")
            
            # Ensure email_verified is False
            if org.email_verified:
                org.email_verified = False
                db.commit()
                print("✅ Reset email_verified to False")
        else:
            print("❌ User not found in database")
            return
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    finally:
        db.close()
    
    # Step 3: Attempt to login with unverified email
    print("\n🔑 Step 3: Attempting login with unverified email...")
    try:
        login_data = {
            'email': test_user['email'],
            'password': test_user['password']
        }
        
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401 and "Email not verified" in response.text:
            print("✅ Test passed: Login blocked for unverified email as expected")
        else:
            print("❌ Test failed: Unverified email login was not blocked properly")
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Unverified login test completed!")

if __name__ == "__main__":
    test_unverified_login()