#!/usr/bin/env python

import unittest
import os
import sys
import json
from decimal import Decimal
from tests.test_secure_computation_flow import TestSecureComputationFlow
from smpc_protocol import SMPCProtocol

class TestSMPCProtocol(unittest.TestCase):
    def setUp(self):
        self.threshold = 2
        self.smpc = SMPCProtocol(threshold=self.threshold)
        self.test_value = Decimal('123.45')
        self.num_shares = 3
    
    def test_secret_sharing(self):
        # Test generating and reconstructing shares
        shares = self.smpc.generate_shares(self.test_value, self.num_shares)
        self.assertEqual(len(shares), self.num_shares)
        
        # Reconstruct from all shares
        reconstructed = self.smpc.reconstruct_secret(shares)
        self.assertEqual(reconstructed, self.test_value)
        
        # Reconstruct from threshold shares
        threshold_shares = shares[:self.threshold]
        reconstructed = self.smpc.reconstruct_secret(threshold_shares)
        self.assertEqual(reconstructed, self.test_value)
    
    def test_secure_sum(self):
        # Test secure sum computation
        values = [Decimal('10.5'), Decimal('20.75'), Decimal('30.25')]
        expected_sum = sum(values)
        
        # Compute secure sum
        result = self.smpc.secure_sum(values)
        self.assertAlmostEqual(result, expected_sum, places=4)
    
    def test_secure_mean(self):
        # Test secure mean computation
        values = [Decimal('10.5'), Decimal('20.75'), Decimal('30.25')]
        expected_mean = sum(values) / len(values)
        
        # Compute secure mean
        result = self.smpc.secure_mean(values)
        self.assertAlmostEqual(result, expected_mean, places=4)
    
    def test_secure_variance(self):
        # Test secure variance computation
        values = [Decimal('10.5'), Decimal('20.75'), Decimal('30.25')]
        mean = sum(values) / len(values)
        expected_variance = sum((v - mean) ** 2 for v in values) / len(values)
        
        # Compute secure variance
        result = self.smpc.secure_variance(values)
        self.assertAlmostEqual(result, expected_variance, places=4)

def run_tests():
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the secure computation flow test
    test_suite.addTest(unittest.makeSuite(TestSecureComputationFlow))
    
    # Add the SMPC protocol test
    test_suite.addTest(unittest.makeSuite(TestSMPCProtocol))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running secure computation flow tests...")
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)