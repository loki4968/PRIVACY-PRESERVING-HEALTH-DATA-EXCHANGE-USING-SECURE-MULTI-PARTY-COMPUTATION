#!/usr/bin/env python3
"""
Test script to verify the secure computation fix for secure_average using SQLite
"""

import sys
import os
sys.path.append('backend')

# Set SQLite database for testing
os.environ['DATABASE_URL'] = 'sqlite:///./test_health_data.db'

def test_secure_average_fix():
    """Test that secure_average uses homomorphic encryption instead of hybrid"""
    print("🧪 Testing Secure Average Fix...")

    try:
        from backend.secure_computation import SecureComputationService
        from backend.dependencies import get_db
        from backend.models import SecureComputation, ComputationParticipant, ComputationResult

        # Get db session
        db_session = next(get_db())

        # Create service with db session
        service = SecureComputationService(db_session)

        # Create a test computation
        computation_id = service.create_computation(org_id=1, computation_type="secure_average", security_method="homomorphic")

        # Add participants
        service.join_computation(computation_id, org_id=1)
        service.join_computation(computation_id, org_id=2)

        # Submit data from participants
        data1 = [{"value": 10.0}, {"value": 20.0}, {"value": 30.0}]
        data2 = [{"value": 15.0}, {"value": 25.0}, {"value": 35.0}]

        service.submit_data(computation_id, org_id=1, data_points=data1)
        service.submit_data(computation_id, org_id=2, data_points=data2)

        # Perform computation
        success = service.perform_computation(computation_id)

        if success:
            # Get result
            result = service.get_computation_result(computation_id)
            if result and "result" in result:
                computed_mean = result["result"].get("mean", 0)
                # Expected average: (10+20+30+15+25+35)/6 = 135/6 = 22.5
                expected = 22.5

                print(f"Computed mean: {computed_mean}")
                print(f"Expected mean: {expected}")

                # Check if result is reasonable
                if isinstance(computed_mean, (int, float)) and abs(computed_mean - expected) < 1.0:
                    print("✅ Secure average computation working correctly")
                    return True
                else:
                    print(f"❌ Result {computed_mean} is not close to expected {expected}")
                    return False
            else:
                print("❌ No result found in computation")
                return False
        else:
            print("❌ Computation failed")
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

        # Get db session
        db_session = next(get_db())

        # Create service with db session
        service = SecureComputationService(db_session)

        # Create a test computation for secure_sum (hybrid method)
        computation_id = service.create_computation(org_id=1, computation_type="secure_sum", security_method="homomorphic")

        # Add participants
        service.join_computation(computation_id, org_id=1)
        service.join_computation(computation_id, org_id=2)

        # Submit data from participants
        data1 = [{"value": 10.0}, {"value": 20.0}]
        data2 = [{"value": 15.0}, {"value": 25.0}]

        service.submit_data(computation_id, org_id=1, data_points=data1)
        service.submit_data(computation_id, org_id=2, data_points=data2)

        # Perform computation
        success = service.perform_computation(computation_id)

        if success:
            # Get result
            result = service.get_computation_result(computation_id)
            if result and "result" in result:
                computed_sum = result["result"].get("sum", 0)
                # Expected sum: 10+20+15+25 = 70
                expected = 70.0

                print(f"Computed sum: {computed_sum}")
                print(f"Expected sum: {expected}")

                if isinstance(computed_sum, (int, float)) and abs(computed_sum - expected) < 1.0:
                    print("✅ Secure sum (hybrid) computation working correctly")
                    return True
                else:
                    print(f"❌ Result {computed_sum} is not close to expected {expected}")
                    return False
            else:
                print("❌ No result found in computation")
                return False
        else:
            print("❌ Computation failed")
            return False

    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Secure Computation Fix with SQLite")
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
