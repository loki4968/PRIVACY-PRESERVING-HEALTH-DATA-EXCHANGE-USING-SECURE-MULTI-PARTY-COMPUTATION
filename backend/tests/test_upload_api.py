import requests
import os
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{API_BASE_URL}/login"
UPLOAD_URL = f"{API_BASE_URL}/upload"
TEST_FILE = "test_upload.csv"  # Use an existing sample file

# Test credentials
TEST_EMAIL = "test@hospital.com"
TEST_PASSWORD = "test123"

def get_auth_token():
    """Get authentication token by logging in"""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        # The API expects form data, not JSON
        response = requests.post(LOGIN_URL, data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print("Login successful!")
            print(f"Response: {token_data}")
            # The token is in the access_token field
            return token_data.get("access_token")
        else:
            print(f"Login failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_upload():
    """Test the upload endpoint"""
    print(f"Testing upload endpoint with file: {TEST_FILE}")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Cannot proceed with upload test without authentication token")
        return
    
    # Check if file exists
    if not os.path.exists(TEST_FILE):
        print(f"Error: Test file {TEST_FILE} not found")
        return
    
    # Prepare the request
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Force-Upload": "true"
    }
    
    files = {
        "file": (os.path.basename(TEST_FILE), open(TEST_FILE, "rb"), "text/csv")
    }
    
    data = {
        "category": "vital_signs"
    }
    
    try:
        # Send the request
        print("Sending request...")
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
        
        # Print response details
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        try:
            response_json = response.json()
            print(f"Response body: {json.dumps(response_json, indent=2)}")
        except ValueError:
            print(f"Response body: {response.text}")
        
        # Check if successful
        if response.status_code == 200 or response.status_code == 201:
            print("Upload successful!")
            try:
                result = response.json()
                if "id" in result:
                    print(f"Upload ID: {result['id']}")
                elif "result_id" in result:
                    print(f"Result ID: {result['result_id']}")
            except ValueError:
                print("Could not parse JSON response")
        else:
            print(f"Upload failed with status code {response.status_code}")
    
    except Exception as e:
        print(f"Error during upload: {e}")
    
    finally:
        # Close the file
        files["file"][1].close()

if __name__ == "__main__":
    test_upload()