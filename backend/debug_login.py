#!/usr/bin/env python3
"""
Script to debug login issues
"""

import requests
import json

def test_all_credentials():
    """Test all possible credentials"""
    base_url = "http://127.0.0.1:8000"
    
    # All possible credentials from the database
    test_credentials = [
        {"email": "lokichowdaryt@gmail.com", "password": "test123"},
        {"email": "test@hospital.com", "password": "test123"},
        {"email": "test@lab.com", "password": "test123"},
        {"email": "test@pharmacy.com", "password": "test123"},
    ]
    
    print("🔍 Testing all possible login credentials...")
    print("=" * 60)
    
    for i, creds in enumerate(test_credentials, 1):
        print(f"\n📋 Test {i}: {creds['email']}")
        print("-" * 40)
        
        try:
            # Test login
            response = requests.post(
                f"{base_url}/login",
                data=creds,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
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
                    print(f"❌ /me failed: {me_response.status_code} - {me_response.text}")
                
            else:
                print(f"❌ Login failed")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Use the credentials that show 'Login successful!'")

if __name__ == "__main__":
    test_all_credentials()
