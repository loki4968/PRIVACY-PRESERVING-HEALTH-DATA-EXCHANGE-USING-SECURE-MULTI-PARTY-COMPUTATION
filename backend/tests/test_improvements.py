#!/usr/bin/env python3
"""
Test script to verify the improvements made to the health data exchange platform.
This script tests error handling, security middleware, and configuration.
"""

import requests
import json
import time
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import settings

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid requests"""
    print("🔍 Testing error handling...")
    
    # Test invalid endpoint
    try:
        response = requests.get(f"{BASE_URL}/invalid-endpoint")
        if response.status_code == 404:
            data = response.json()
            if "error" in data and "code" in data["error"]:
                print("✅ 404 error handling working correctly")
            else:
                print("❌ 404 error response format incorrect")
                return False
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    return True

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("🔍 Testing rate limiting...")
    
    # Make multiple requests quickly to trigger rate limiting
    responses = []
    for i in range(65):  # More than the 60 per minute limit
        try:
            response = requests.get(f"{BASE_URL}/health")
            responses.append(response.status_code)
            if response.status_code == 429:
                print(f"✅ Rate limiting triggered after {i+1} requests")
                return True
        except Exception as e:
            print(f"❌ Rate limiting test error: {e}")
            return False
    
    print("❌ Rate limiting not triggered")
    return False

def test_security_headers():
    """Test security headers"""
    print("🔍 Testing security headers...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        headers = response.headers
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        missing_headers = []
        for header in required_headers:
            if header not in headers:
                missing_headers.append(header)
        
        if missing_headers:
            print(f"❌ Missing security headers: {missing_headers}")
            return False
        else:
            print("✅ All security headers present")
            return True
            
    except Exception as e:
        print(f"❌ Security headers test error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    
    try:
        # Test that settings are loaded correctly
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'UPLOAD_DIR')
        assert hasattr(settings, 'RATE_LIMIT_PER_MINUTE')
        
        print("✅ Configuration loaded correctly")
        print(f"   App Name: {settings.APP_NAME}")
        print(f"   Database: {settings.DATABASE_URL}")
        print(f"   Upload Dir: {settings.UPLOAD_DIR}")
        print(f"   Rate Limit: {settings.RATE_LIMIT_PER_MINUTE}/min")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoint"""
    print("🔍 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Health Data Exchange Platform Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Health Endpoint", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Error Handling", test_error_handling),
        ("Security Headers", test_security_headers),
        ("API Documentation", test_api_documentation),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The improvements are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
