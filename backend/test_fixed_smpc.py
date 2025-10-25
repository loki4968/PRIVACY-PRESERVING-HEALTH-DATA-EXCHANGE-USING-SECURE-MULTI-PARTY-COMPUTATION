#!/usr/bin/env python3
"""
Test script to verify the SMPC coefficient fix produces reasonable values
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from smpc_protocols import SMPCProtocol
from decimal import Decimal

def test_smpc_shares():
    """Test SMPC share generation and reconstruction"""
    print("🧪 Testing SMPC Share Generation")
    print("=" * 50)
    
    # Initialize SMPC protocol
    smpc = SMPCProtocol()
    
    # Test with small values similar to health data
    test_values = [1.0, 2.0, 3.0, 100.5, 98.6, 120.3]
    
    print(f"📊 Test values: {test_values}")
    
    for i, value in enumerate(test_values):
        print(f"\n🔍 Testing value {i+1}: {value}")
        
        # Generate shares
        shares = smpc.generate_shares(value, 3, 2)
        print(f"  Generated {len(shares)} shares")
        
        # Check share values
        share_values = [float(share['value']) for share in shares]
        print(f"  Share values: {share_values}")
        
        # Check if values are reasonable (not astronomically large)
        max_share = max(abs(v) for v in share_values)
        if max_share > 1e10:
            print(f"  ⚠️ WARNING: Large share value detected: {max_share}")
        else:
            print(f"  ✅ Share values are reasonable (max: {max_share})")
        
        # Test reconstruction
        try:
            reconstructed = smpc.reconstruct_secret(shares)
            reconstructed_float = float(reconstructed)
            error = abs(reconstructed_float - value)
            
            print(f"  Original: {value}")
            print(f"  Reconstructed: {reconstructed_float}")
            print(f"  Error: {error}")
            
            if error < 0.001:
                print(f"  ✅ Reconstruction successful")
            else:
                print(f"  ❌ Reconstruction error too large")
                
        except Exception as e:
            print(f"  ❌ Reconstruction failed: {e}")
    
    # Test secure sum
    print(f"\n🧮 Testing secure sum")
    try:
        secure_sum_result = smpc.secure_sum(test_values)
        expected_sum = sum(test_values)
        error = abs(float(secure_sum_result) - expected_sum)
        
        print(f"  Expected sum: {expected_sum}")
        print(f"  Secure sum: {float(secure_sum_result)}")
        print(f"  Error: {error}")
        
        if error < 0.001:
            print(f"  ✅ Secure sum successful")
        else:
            print(f"  ❌ Secure sum error too large")
            
    except Exception as e:
        print(f"  ❌ Secure sum failed: {e}")
    
    # Test secure mean
    print(f"\n📊 Testing secure mean")
    try:
        secure_mean_result = smpc.secure_mean(test_values)
        expected_mean = sum(test_values) / len(test_values)
        error = abs(float(secure_mean_result) - expected_mean)
        
        print(f"  Expected mean: {expected_mean}")
        print(f"  Secure mean: {float(secure_mean_result)}")
        print(f"  Error: {error}")
        
        if error < 0.001:
            print(f"  ✅ Secure mean successful")
        else:
            print(f"  ❌ Secure mean error too large")
            
    except Exception as e:
        print(f"  ❌ Secure mean failed: {e}")

def main():
    """Main test function"""
    test_smpc_shares()
    
    print("\n" + "=" * 50)
    print("🧪 SMPC testing complete!")

if __name__ == "__main__":
    main()
