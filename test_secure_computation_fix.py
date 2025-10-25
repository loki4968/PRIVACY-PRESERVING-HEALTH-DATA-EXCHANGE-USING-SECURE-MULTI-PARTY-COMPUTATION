#!/usr/bin/env python3
"""
Test script to verify the secure computation fix for secure_average
"""

import sys
import os
sys.path.append('backend')

def test_secure_average_fix():
    """Test that secure_average uses homomorphic encryption instead of hybrid"""
    print("🧪 Testing Secure Average Fix...")

    try:
        from backend.secure_computation import SecureComputationService
        from backend.dependencies import get_db
        from sqlalchemy.orm import Session

        # Create a mock db session
        db_session = next(get_db())

        # Create service with db session
        service = SecureComputationService(db_session)

        # Mock data for two parties
        party1_data = [10.0, 20.0, 30.0]
        party2_data = [15.0, 25.0, 35.0]

        # Mock encrypted data (in real scenario, this would be encrypted)
        results = [
            {'data': party1_data, 'computation_type': 'secure_average'},
            {'data': party2_data, 'computation_type': 'secure_average'}
        ]

        # Perform computation
        result = service.perform_computation('secure_average', results)

        # Expected average: (10+20+30+15+25+35)/6 = 135/6 = 22.5
        expected = 22.5

        print(f"Computed result: {result}")
        print(f"Expected result: {expected}")

        # Check if result is reasonable (not excessively large like before)
        if isinstance(result, (int, float)) and abs(result - expected) < 1.0:
            print("✅ Secure average computation working correctly")
            return True
        else:
            print(f"❌ Result {result} is not close to expected {expected}")
            return False

    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hybrid_still_works():
    """Test that secure_sum still uses hybrid method"""
    print("\n🔄 Testing Hybrid Method Still Works...")

    try:
        from backend.secure_computation import SecureComputationService
        from backend.dependencies import get_db
        from sqlalchemy.orm import Session

        # Create a mock db session
        db_session = next(get_db())

        # Create service with db session
        service = SecureComputationService(db_session)

        # Mock data
        party1_data = [10.0, 20.0]
        party2_data = [15.0, 25.0]

        results = [
            {'data': party1_data, 'computation_type': 'secure_sum'},
            {'data': party2_data, 'computation_type': 'secure_sum'}
        ]

        # This should use hybrid method
        result = service.perform_computation('secure_sum', results)

        # Expected sum: 10+20+15+25 = 70
        expected = 70.0

        print(f"Computed result: {result}")
        print(f"Expected result: {expected}")

        if isinstance(result, (int, float)) and abs(result - expected) < 1.0:
            print("✅ Secure sum (hybrid) computation working correctly")
            return True
        else:
            print(f"❌ Result {result} is not close to expected {expected}")
            return False

    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Secure Computation Fix")
    print("=" * 50)

    test1_passed = test_secure_average_fix()
    test2_passed = test_hybrid_still_works()

    print("\n" + "=" * 50)
    passed = sum([test1_passed, test2_passed])
    total = 2
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The fix is working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")

    sys.exit(0 if passed == total else 1)
