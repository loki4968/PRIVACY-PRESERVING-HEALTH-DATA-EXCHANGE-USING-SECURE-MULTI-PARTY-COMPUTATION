import requests
import json

def test_formdata_upload():
    print('Testing FormData upload with authentication token:')
    
    # Step 1: Login to get a valid token
    login_url = 'http://localhost:8000/login'
    login_data = {
        'email': 'test@hospital.com',
        'password': 'test123'
    }
    
    try:
        # Get authentication token
        login_response = requests.post(login_url, data=login_data)
        if login_response.status_code != 200:
            print(f'Login failed: {login_response.status_code}')
            print(f'Response: {login_response.text}')
            return
            
        token_data = login_response.json()
        token = token_data.get('access_token')
        
        if not token:
            print('No token received from login')
            return
            
        print(f'Successfully logged in and received token')
        
        # Step 2: Try to upload a file with the token using FormData-like structure
        upload_url = 'http://localhost:8000/upload'
        
        # Create a simple test file
        test_file_path = 'test_formdata_upload.csv'
        with open(test_file_path, 'w') as f:
            f.write('date,value\n2023-01-01,120\n2023-01-02,122')
        
        # Prepare the upload request - similar to FormData in browser
        files = {'file': ('test_formdata_upload.csv', open(test_file_path, 'rb'), 'text/csv')}
        data = {'category': 'vital_signs'}
        headers = {
            'Authorization': f'Bearer {token}',
            # No Content-Type header - let requests set it with boundary
            'X-Force-Upload': 'true'
        }
        
        # Send the upload request
        upload_response = requests.post(upload_url, files=files, data=data, headers=headers)
        
        print(f'Upload status code: {upload_response.status_code}')
        print(f'Upload response: {upload_response.text}')
        
        # Close the file
        files['file'][1].close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_formdata_upload()