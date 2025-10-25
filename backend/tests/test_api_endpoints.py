from fastapi.testclient import TestClient
from fastapi import status
import pytest
from datetime import datetime
from main import app

# Create test client
client = TestClient(app)

def test_api_routes_exist():
    """Test that the API routes with /api prefix exist"""
    # Make a request to a non-existent endpoint with the /api prefix
    response = client.post(
        "/api/report-requests/access-by-code",
        json={"secret_code": "NONEXISTENT"}
    )
    
    # We expect a 404 because the secret code doesn't exist, but the route should be found
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # Print response for debugging
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.json() if response.status_code != 500 else response.text}")
    # The error message might be in different formats, so we'll just check the status code
    
    # Make a request to the same endpoint without the /api prefix
    response = client.post(
        "/report-requests/access-by-code",
        json={"secret_code": "NONEXISTENT"}
    )
    
    # We expect a 404 but for a different reason - the route doesn't exist
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Print all routes for debugging
    print("\nAll routes:")
    for route in app.routes:
        methods = getattr(route, 'methods', ['N/A'])
        print(f"  {route.path} [{methods}]")
    
    # Check for specific routes with /api prefix
    api_routes = [route for route in app.routes if str(route.path).startswith('/api')]
    report_request_routes = [route for route in api_routes if 'report-requests' in str(route.path)]
    
    print("\nReport request routes with /api prefix:")
    for route in report_request_routes:
        methods = getattr(route, 'methods', ['N/A'])
        print(f"  {route.path} [{methods}]")
    
    # Assert that we have at least one report-requests route with /api prefix
    assert len(report_request_routes) > 0, "No report-requests routes found with /api prefix"
    
    # Check for specific routes
    access_by_code_route = any('/api/report-requests/access-by-code' in str(route.path) for route in report_request_routes)
    download_by_code_route = any('/api/report-requests/download-by-code' in str(route.path) for route in report_request_routes)
    
    assert access_by_code_route, "access-by-code route not found with /api prefix"
    assert download_by_code_route, "download-by-code route not found with /api prefix"