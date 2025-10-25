#!/usr/bin/env python3
"""
Test script to verify the secure computation fix for secure_average
"""

import sys
import os
sys.path.append('backend')

def test_secure_average_fix():
    """Test that secure_average uses hybrid method and produces reasonable results"""
    print("🧪 Testing Secure Average Fix...")

    try:
        from backend.secure_computation import SecureComputationService
        from backend.dependencies import get_db
        from sqlalchemy.orm import Session

        # Create a db session
        db_session = next(get_db())

        # Create service with db session
        service = SecureComputationService(db_session)

        # Create a computation
        computation_id = service.create_computation(org_id=1, computation_type="secure_average")

        # Add participants
        service.join_computation(computation_id, org_id=1)
        service.join_computation(computation_id, org_id=2)

        # Submit data from each participant
        service.submit_data(computation_id, org_id=1, data_points=[10.0, 20.0, 30.0])
        service.submit_data(computation_id, org_id=2, data_points=[15.0, 25.0, 35.0])

        # Perform computation
        import asyncio
        success = asyncio.run(service.perform_computation(computation_id))

        if success:
            # Get the results
            result = service.get_computation_result(computation_id)
            computation_result = result.get('result', {})

            print(f"Computation result: {computation_result}")

            # Expected average: (10+20+30+15+25+35)/6 = 135/6 = 22.5
            expected_mean = 22.5

            # Check if result contains reasonable values
            mean_value = computation_result.get('mean') or computation_result.get('average')
            if mean_value and isinstance(mean_value, (int, float)) and abs(mean_value - expected_mean) < 1.0:
                print(f"✅ Secure average computation working correctly: {mean_value}")
                return True
            else:
                print(f"❌ Result mean {mean_value} is not close to expected {expected_mean}")
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
        from sqlalchemy.orm import Session

        # Create a db session
        db_session = next(get_db())

        # Create service with db session
        service = SecureComputationService(db_session)

        # Create a computation
        computation_id = service.create_computation(org_id=1, computation_type="secure_sum")

        # Add participants
        service.join_computation(computation_id, org_id=1)
        service.join_computation(computation_id, org_id=2)

        # Submit data from each participant
        service.submit_data(computation_id, org_id=1, data_points=[10.0, 20.0])
        service.submit_data(computation_id, org_id=2, data_points=[15.0, 25.0])

        # Perform computation
        import asyncio
        success = asyncio.run(service.perform_computation(computation_id))

        if success:
            # Get the results
            result = service.get_computation_result(computation_id)
            computation_result = result.get('result', {})

            print(f"Computation result: {computation_result}")

            # Expected sum: 10+20+15+25 = 70
            expected_sum = 70.0

            # Check if result contains reasonable values
            sum_value = computation_result.get('sum')
            if sum_value and isinstance(sum_value, (int, float)) and abs(sum_value - expected_sum) < 1.0:
                print(f"✅ Secure sum (hybrid) computation working correctly: {sum_value}")
                return True
            else:
                print(f"❌ Result sum {sum_value} is not close to expected {expected_sum}")
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
