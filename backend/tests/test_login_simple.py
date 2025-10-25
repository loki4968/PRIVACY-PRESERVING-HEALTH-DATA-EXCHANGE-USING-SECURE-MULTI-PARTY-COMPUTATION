#!/usr/bin/env python3
"""
Simple login test to debug the issue
"""

import requests

def test_login():
    """Test login with known credentials"""
    base_url = "http://127.0.0.1:8000"
    
    # Test with a known working account
    test_credentials = {
        "email": "test@hospital.com",
        "password": "test123"
    }
    
    print("🔍 Testing Login...")
    print("=" * 50)
    print(f"Email: {test_credentials['email']}")
    print(f"Password: {test_credentials['password']}")
    print("-" * 50)
    
    try:
        # Test login
        response = requests.post(
            f"{base_url}/login",
            data=test_credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Token Type: {data.get('token_type')}")
            print(f"Access Token: {data.get('access_token')[:20]}...")
            
            # Test /me endpoint
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            me_response = requests.get(f"{base_url}/me", headers=headers)
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ User info: {user_data['name']} ({user_data['role']})")
            else:
                print(f"❌ /me failed: {me_response.status_code} - {me_response.text}")
        else:
            print("❌ Login failed!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_login()
