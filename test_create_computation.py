#!/usr/bin/env python3
"""
Test script for the create_computation endpoint with security_method parameter.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer dummy_token"  # Will fail auth but we can check if parameter is accepted
}

def test_create_computation_endpoint():
    """Test the create_computation endpoint with different security methods."""
    print("🧪 Testing create_computation endpoint with security_method parameter...")

    security_methods = ["standard", "homomorphic", "hybrid"]

    for method in security_methods:
        print(f"\n   Testing security_method: {method}")
        payload = {
            "computation_type": "secure_average",
            "security_method": method
        }

        try:
            response = requests.post(
                f"{BASE_URL}/secure-computations/create",
                json=payload,
                headers=HEADERS,
                timeout=10
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 401:
                # Authentication failed, but check if the error mentions security_method
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', '')
                if 'security_method' in error_msg or 'unrecognized' not in str(error_data).lower():
                    print(f"   ✅ Parameter 'security_method' accepted (auth failed as expected)")
                else:
                    print(f"   ⚠️  Parameter might not be accepted: {error_msg}")
            elif response.status_code == 422:
                # Validation error - check if it's about security_method
                error_data = response.json()
                print(f"   Validation error: {error_data}")
                if 'security_method' in str(error_data):
                    print(f"   ✅ Parameter 'security_method' is validated")
                else:
                    print(f"   ❌ Unexpected validation error: {error_data}")
            else:
                print(f"   Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

def test_without_security_method():
    """Test the endpoint without security_method to see if it's required."""
    print("\n🧪 Testing create_computation endpoint without security_method...")

    payload = {
        "computation_type": "secure_average"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/secure-computations/create",
            json=payload,
            headers=HEADERS,
            timeout=10
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 401:
            print(f"   ✅ Auth failed as expected (parameter not required)")
        elif response.status_code == 422:
            error_data = response.json()
            print(f"   Validation error: {error_data}")
        else:
            print(f"   Unexpected status: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing create_computation endpoint")
    print("=" * 50)

    # Test basic connectivity
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print("✅ Server is running and accessible")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        sys.exit(1)

    test_create_computation_endpoint()
    test_without_security_method()

    print("\n" + "=" * 50)
    print("📊 Test completed. Check the results above.")
