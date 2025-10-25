#!/usr/bin/env python3
"""
Test script for ML endpoints in the secure computation system.
This script tests the new advanced ML capabilities.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test_token"  # This will need to be updated with a real token
}

def test_performance_metrics():
    """Test the performance metrics endpoint."""
    print("🧪 Testing performance metrics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/secure-computations/performance/metrics", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_available_algorithms():
    """Test the available ML algorithms endpoint."""
    print("🧪 Testing available ML algorithms endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/secure-computations/ml/available-algorithms", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Available algorithms: {list(data.get('algorithms', {}).keys())}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_system_info():
    """Test the system information endpoint."""
    print("🧪 Testing system information endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/secure-computations/performance/system-info", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System info retrieved successfully")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_cache_stats():
    """Test the cache statistics endpoint."""
    print("🧪 Testing cache statistics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/secure-computations/performance/cache-stats", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Cache stats retrieved successfully")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_memory_efficient_mode():
    """Test enabling memory-efficient mode."""
    print("🧪 Testing memory-efficient mode endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/secure-computations/performance/enable-memory-efficient",
            json={"chunk_size": 500},
            timeout=10
        )
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Memory-efficient mode enabled: {data.get('message', '')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_clear_cache():
    """Test clearing the cache."""
    print("🧪 Testing cache clearing endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/secure-computations/performance/clear-cache", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Cache cleared: {data.get('message', '')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_available_computations():
    """Test the available computations endpoint."""
    print("🧪 Testing available computations endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/secure-computations/available-computations", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Available computations: {len(data.get('computations', {}))} types")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_list_organizations():
    """Test the organizations listing endpoint."""
    print("🧪 Testing organizations listing endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/secure-computations/organizations", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} organizations")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting ML Endpoints Tests")
    print("=" * 50)

    # Test basic connectivity first
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print("✅ Server is running and accessible")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("Please ensure the server is running with: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)

    tests = [
        test_performance_metrics,
        test_available_algorithms,
        test_system_info,
        test_cache_stats,
        test_memory_efficient_mode,
        test_clear_cache,
        test_available_computations,
        test_list_organizations
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            print()

        # Small delay between tests
        time.sleep(1)

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed successfully!")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
