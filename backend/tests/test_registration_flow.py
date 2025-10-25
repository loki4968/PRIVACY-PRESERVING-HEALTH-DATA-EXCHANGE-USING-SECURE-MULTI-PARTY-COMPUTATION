#!/usr/bin/env python3
"""
Test the complete registration and OTP flow
"""

import requests
import json
import time

def test_registration_flow():
    """Test the complete registration and OTP flow"""
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 Testing Complete Registration and OTP Flow")
    print("=" * 60)
    
    # Test data - use a unique email
    import random
    unique_id = random.randint(1000, 9999)
    test_email = f"test{unique_id}@hospital.com"
    
    test_user = {
        "name": f"Test Hospital {unique_id}",
        "email": test_email,
        "contact": "+1-555-0123",
        "type": "HOSPITAL",
        "location": "New York, NY",
        "password": "test123",
        "privacy_accepted": True
    }
    
    print(f"📧 Using test email: {test_email}")
    print("-" * 50)
    
    # Step 1: Register organization
    print("📝 Step 1: Registering organization...")
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
            
            # Get the OTP from storage (for testing)
            from otp_utils import get_stored_otp
            stored_otp = get_stored_otp(test_user['email'])
            if stored_otp:
                print(f"🔐 [DEV] OTP is: {stored_otp}")
            else:
                print("❌ OTP not found in storage!")
                return
        else:
            print("❌ Failed to send OTP!")
            return
            
    except Exception as e:
        print(f"❌ OTP sending error: {e}")
        return
    
    # Step 3: Verify OTP
    print(f"\n🔐 Step 3: Verifying OTP...")
    try:
        verify_data = {
            "email": test_user['email'],
            "otp": stored_otp
        }
        
        response = requests.post(
            f"{base_url}/verify-otp",
            json=verify_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ OTP verified successfully!")
        else:
            print("❌ OTP verification failed!")
            return
            
    except Exception as e:
        print(f"❌ OTP verification error: {e}")
        return
    
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
                print(f"✅ Email verified: {user_data.get('email_verified', 'N/A')}")
            else:
                print(f"❌ /me failed: {me_response.status_code}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Registration and OTP flow test completed!")

if __name__ == "__main__":
    test_registration_flow()
