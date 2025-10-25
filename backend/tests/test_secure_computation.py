import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test error handling for various scenarios
def test_error_handling():
    print("\n=== Testing Error Handling for Secure Computations ===")
    
    # Test 1: Create a computation without authentication
    print("\n=== Test 1: Create computation without authentication ===")
    payload = {
        "computation_type": "test_metrics",
        "participating_orgs": ["1", "2", "3"]
    }
    response = requests.post(f"{BASE_URL}/computations?org_id=1&computation_type=health_metrics", json=payload)
    print(f"Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test 2: Get computation with invalid ID
    print("\n=== Test 2: Get computation with invalid ID ===")
    response = requests.get(f"{BASE_URL}/computations/999999/result?org_id=1")
    print(f"Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test 3: Compute result with invalid ID
    print("\n=== Test 3: Compute result with invalid ID ===")
    response = requests.post(f"{BASE_URL}/computations/999999/compute?org_id=1")
    print(f"Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test 4: Submit data with invalid ID
    print("\n=== Test 4: Submit data with invalid ID ===")
    payload = [100, 120, 130]
    response = requests.post(f"{BASE_URL}/computations/999999/submit?org_id=1", json=payload)
    print(f"Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test 5: List all computations
    print("\n=== Test 5: List all computations ===")
    response = requests.get(f"{BASE_URL}/computations?org_id=1")
    print(f"Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

# Run the tests
if __name__ == "__main__":
    test_error_handling()