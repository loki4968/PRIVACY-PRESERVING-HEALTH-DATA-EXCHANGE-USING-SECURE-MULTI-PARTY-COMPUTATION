from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

def test_api_routes_exist():
    # Test that the routes with /api prefix exist
    
    # We'll just check if the routes exist by examining the app's routes
    api_routes = [route for route in app.routes if str(route.path).startswith('/api')]
    
    # Check if our specific routes exist
    report_request_routes = [route for route in api_routes if 'report-requests' in str(route.path)]
    
    # Print all routes for debugging
    print("\nAll API routes:")
    for route in api_routes:
        print(f"  {route.path} [{route.methods}]")
    
    print("\nReport request routes:")
    for route in report_request_routes:
        print(f"  {route.path} [{route.methods}]")
    
    # Assert that we have at least one report-requests route with /api prefix
    assert len(report_request_routes) > 0, "No report-requests routes found with /api prefix"
    
    # Check for specific routes
    access_by_code_route = any('/api/report-requests/access-by-code' in str(route.path) for route in report_request_routes)
    download_by_code_route = any('/api/report-requests/download-by-code' in str(route.path) for route in report_request_routes)
    
    assert access_by_code_route, "access-by-code route not found with /api prefix"
    assert download_by_code_route, "download-by-code route not found with /api prefix"