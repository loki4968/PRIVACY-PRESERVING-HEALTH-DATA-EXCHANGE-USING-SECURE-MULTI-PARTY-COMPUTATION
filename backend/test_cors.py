import requests

def test_cors():
    print('Testing CORS configuration:')
    try:
        r = requests.options('http://localhost:8000/upload', 
                            headers={'Origin': 'http://localhost:3000'})
        print(f'Status: {r.status_code}')
        print(f'Headers: {dict(r.headers)}')
        
        if 'access-control-allow-origin' in r.headers:
            print('CORS is properly configured')
        else:
            print('CORS headers missing - this could cause frontend fetch issues')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_cors()