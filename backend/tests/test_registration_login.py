import requests
import json
import random
import string
import time
from models import SessionLocal, Organization

# Base URL for API
base_url = "http://localhost:8000"

def generate_test_user():
    """Generate random test user data"""
    random_suffix = ''.join(random.choices(string.digits, k=6))
    return {
        'name': f"Test User {random_suffix}",
        'email': f"test-user-{random_suffix}@example.com",
        'contact': f"555-{random_suffix}",
        'type': "HOSPITAL",
        'location': "Test Location",
        'password': f"TestPass123{random_suffix}",
        'privacy_accepted': True
    }

def test_registration_login_flow():
    """Test the complete registration and login flow"""
    print("🧪 Testing Registration and Login Flow")
    print("=" * 80)
    
    # Step 1: Generate test user
    test_user = generate_test_user()
    print(f"\n📝 Step 1: Registering test user: {test_user['email']}")
    
    # Step 2: Register user
    try:
        register_data = {
            'name': test_user['name'],
            'email': test_user['email'],
            'contact': test_user['contact'],
            'type': test_user['type'],
            'location': test_user['location'],
            'password': test_user['password'],
            'privacy_accepted': test_user['privacy_accepted']
        }
        
        response = requests.post(
            f"{base_url}/register",
            data=register_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Step 3: Verify user in database and set email_verified=True
    print("\n🔍 Step 3: Verifying user in database...")
    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.email == test_user['email']).first()
        if org:
            print(f"✅ User found in database")
            print(f"✅ Email verified status: {org.email_verified}")
            
            # Set email_verified to True for testing
            if not org.email_verified:
                org.email_verified = True
                db.commit()
                print("✅ Set email_verified to True")
        else:
            print("❌ User not found in database")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        db.close()
    
    # Step 4: Test login
    print("\n🔑 Step 4: Testing login...")
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
                return True
            else:
                print(f"❌ /me endpoint failed: {me_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

if __name__ == "__main__":
    # Check if server is running
    try:
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code != 200:
            print("❌ Server is not running or not healthy. Please start the server first.")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        exit(1)
    
    # Run the test
    success = test_registration_login_flow()
    
    if success:
        print("\n✅ Registration and login flow test passed!")
    else:
        print("\n❌ Registration and login flow test failed!")