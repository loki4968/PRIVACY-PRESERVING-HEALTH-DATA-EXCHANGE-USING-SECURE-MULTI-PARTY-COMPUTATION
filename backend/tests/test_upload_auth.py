#!/usr/bin/env python3
"""
Test upload authentication
"""

import requests
import json

def test_upload_with_auth():
    """Test upload with proper authentication"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing Upload Authentication...")
    print("=" * 60)
    
    # Step 1: Login to get token
    print("📝 Step 1: Logging in...")
    login_data = {
        'email': 'exchangehealthdata@gmail.com',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print("✅ Login successful!")
            print(f"Token: {token[:20]}...")
            
            # Step 2: Test upload with token
            print("\n📤 Step 2: Testing upload with token...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'multipart/form-data'
            }
            
            # Create a simple test file
            files = {
                'file': ('test.csv', 'test,data,here', 'text/csv')
            }
            
            data = {
                'category': 'vital_signs'
            }
            
            upload_response = requests.post(
                f"{base_url}/upload",
                files=files,
                data=data,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            print(f"Upload Status: {upload_response.status_code}")
            print(f"Upload Response: {upload_response.text}")
            
            if upload_response.status_code == 200:
                print("✅ Upload successful!")
            else:
                print("❌ Upload failed!")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_upload_without_auth():
    """Test upload without authentication"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔍 Testing Upload WITHOUT Authentication...")
    print("=" * 60)
    
    try:
        # Create a simple test file
        files = {
            'file': ('test.csv', 'test,data,here', 'text/csv')
        }
        
        data = {
            'category': 'vital_signs'
        }
        
        upload_response = requests.post(
            f"{base_url}/upload",
            files=files,
            data=data
        )
        
        print(f"Upload Status: {upload_response.status_code}")
        print(f"Upload Response: {upload_response.text}")
        
        if upload_response.status_code == 401:
            print("✅ Correctly rejected unauthorized upload!")
        else:
            print("❌ Should have been rejected!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_upload_with_auth()
    test_upload_without_auth()
