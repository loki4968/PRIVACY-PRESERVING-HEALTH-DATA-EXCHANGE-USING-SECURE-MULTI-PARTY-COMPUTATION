#!/usr/bin/env python3
"""
Test script to verify the registration flow with the implemented fixes
"""

import requests
import random
import json
import time

def test_new_registration():
    """Test the registration flow with a new user"""
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 Testing New Registration Flow")
    print("=" * 60)
    
    # Test data with random email to avoid conflicts
    random_id = random.randint(100000, 999999)  # Using a larger range to avoid conflicts
    test_email = f"test-new-{random_id}@hospital.com"
    
    test_user = {
        "name": "Test Hospital New",
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
            'privacy_accepted': test_user['privacy_accepted']
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
    
    # Step 2: Send OTP
    print("\n📧 Step 2: Sending OTP...")
    try:
        otp_data = {"email": test_user['email']}
        response = requests.post(
            f"{base_url}/send-otp",
            json=otp_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP sent successfully!")
            
            # For testing purposes, directly update the database to verify the email
            print("⚠️ Bypassing OTP verification for testing...")
            
            # Import database models
            from models import SessionLocal, Organization
            
            # Update the database directly
            db = SessionLocal()
            try:
                org = db.query(Organization).filter(Organization.email == test_user['email']).first()
                if org:
                    org.email_verified = True
                    db.commit()
                    print(f"✅ Email verified directly in database for testing")
                else:
                    print(f"❌ Organization not found in database")
                    return
            except Exception as e:
                print(f"❌ Database update error: {e}")
                db.rollback()
                return
            finally:
                db.close()
                
            # Skip OTP verification step
            print("\n🔐 Step 3: Skipping OTP verification (email verified directly)")
        else:
            print("❌ Failed to send OTP!")
            return
            
    except Exception as e:
        print(f"❌ OTP sending error: {e}")
        return
    
    # Step 3: OTP verification is handled in the previous step
    # If we get here, it means we're skipping to login
    
    # Step 4: Login
    print(f"\n🔑 Step 4: Testing login...")
    try:
        login_data = {
            'email': test_user['email'],
            'password': test_user['password']
        }
        
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Token Type: {data.get('token_type')}")
            print(f"Expires In: {data.get('expires_in')} seconds")
            
            # Test /me endpoint
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            me_response = requests.get(f"{base_url}/me", headers=headers)
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ User info: {user_data['name']} ({user_data['role']})")
            else:
                print(f"❌ Failed to get user info: {me_response.status_code}")
        else:
            print("❌ Login failed!")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎯 Registration flow test completed successfully!")

if __name__ == "__main__":
    test_new_registration()