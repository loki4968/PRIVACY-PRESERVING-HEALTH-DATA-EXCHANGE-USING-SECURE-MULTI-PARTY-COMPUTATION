#!/usr/bin/env python3
"""
Quick authentication test
"""

import requests

def test_auth():
    """Test basic authentication"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Quick Authentication Test")
    print("=" * 40)
    
    # Test with existing user
    test_credentials = {
        "email": "exchangehealthdata@gmail.com",
        "password": "test123"
    }
    
    print(f"Testing login with: {test_credentials['email']}")
    
    try:
        # Test login
        response = requests.post(
            f"{base_url}/login",
            data=test_credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Token: {data.get('access_token', 'N/A')[:20]}...")
            
            # Test /me endpoint
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            me_response = requests.get(f"{base_url}/me", headers=headers)
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ User authenticated: {user_data['name']}")
                print(f"✅ Email verified: {user_data.get('email_verified', 'N/A')}")
                print(f"✅ Role: {user_data.get('role', 'N/A')}")
            else:
                print(f"❌ /me failed: {me_response.status_code}")
        else:
            print("❌ Login failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Start with: python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_auth()
