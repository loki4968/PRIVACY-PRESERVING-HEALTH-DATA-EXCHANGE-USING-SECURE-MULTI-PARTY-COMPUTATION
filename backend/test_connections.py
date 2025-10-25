import requests

def test_connections():
    print('Testing backend and frontend connections:')
    try:
        # Test backend health endpoint
        r = requests.get('http://localhost:8000/health')
        print(f'Backend health: {r.status_code}')
        
        # Test frontend connection
        try:
            r2 = requests.get('http://localhost:3000')
            print(f'Frontend status: {r2.status_code}')
        except Exception as e:
            print(f'Frontend error: {e}')
            
        # Test upload endpoint with OPTIONS request (CORS preflight)
        r3 = requests.options('http://localhost:8000/upload', 
                             headers={'Origin': 'http://localhost:3000'})
        print(f'Upload endpoint CORS: {r3.status_code}')
        
        # Test upload endpoint with a mock POST request
        headers = {
            'Authorization': 'Bearer test_token',
            'Origin': 'http://localhost:3000'
        }
        try:
            r4 = requests.post('http://localhost:8000/upload', headers=headers)
            print(f'Upload endpoint POST: {r4.status_code}')
            print(f'Response: {r4.text[:100]}...')
        except Exception as e:
            print(f'Upload POST error: {e}')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_connections()