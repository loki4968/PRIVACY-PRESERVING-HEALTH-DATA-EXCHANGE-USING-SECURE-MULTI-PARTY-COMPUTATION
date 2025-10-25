from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

def test_api_prefix_for_report_requests():
    # Test that the report-requests endpoints are correctly prefixed with /api
    
    # Test access-by-code endpoint
    response = client.post(
        "/api/report-requests/access-by-code",
        json={"secret_code": "TEST1234"}
    )
    # We expect a 404 because the secret code doesn't exist, but the route should be found
    assert response.status_code != 404 or "No approved report found with this secret code" in response.json().get("detail", "")
    
    # Test download-by-code endpoint
    response = client.get("/api/report-requests/download-by-code/TEST1234")
    # We expect a 404 because the secret code doesn't exist, but the route should be found
    assert response.status_code != 404 or "No approved report found with this secret code" in response.json().get("detail", "")
    
    # Test the same endpoints without the /api prefix to confirm they don't work
    response = client.post(
        "/report-requests/access-by-code",
        json={"secret_code": "TEST1234"}
    )
    # This should return 404 Not Found because the route doesn't exist without the /api prefix
    assert response.status_code == 404
    
    response = client.get("/report-requests/download-by-code/TEST1234")
    # This should return 404 Not Found because the route doesn't exist without the /api prefix
    assert response.status_code == 404