#!/usr/bin/env python3
"""
Health Data Exchange Project Testing Script
Tests core functionality without requiring full deployment
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_imports():
    """Test that all critical modules can be imported"""
    print("🧪 Testing Module Imports...")
    
    try:
        # Test backend imports
        from backend import models
        from backend import auth_utils
        from backend import smpc_protocols
        from backend import secure_computation
        from backend import homomorphic_encryption_enhanced
        from backend import utils
        from backend import encryption
        
        print("✅ All backend modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_smpc_protocols():
    """Test SMPC protocols functionality"""
    print("\n🔐 Testing SMPC Protocols...")
    
    try:
        from backend.smpc_protocols import ShamirSecretSharing, SMPCProtocol
        
        # Test Shamir's Secret Sharing
        sss = ShamirSecretSharing(threshold=3, num_shares=5)
        secret = 12345
        shares = sss.generate_shares(secret)
        reconstructed = sss.reconstruct_secret(shares[:3])
        
        assert reconstructed == secret, f"Expected {secret}, got {reconstructed}"
        print("✅ Shamir's Secret Sharing working correctly")
        
        # Test SMPC Protocol
        protocol = SMPCProtocol(threshold=2, num_parties=3)
        party1_data = [10, 20, 30]
        party2_data = [15, 25, 35]
        
        shares1 = protocol.generate_data_shares(party1_data)
        shares2 = protocol.generate_data_shares(party2_data)
        
        result = protocol.secure_sum([shares1, shares2])
        expected = sum(party1_data) + sum(party2_data)
        
        assert abs(result - expected) < 0.001, f"Expected {expected}, got {result}"
        print("✅ SMPC Protocol working correctly")
        
        return True
    except Exception as e:
        print(f"❌ SMPC test error: {e}")
        traceback.print_exc()
        return False

def test_homomorphic_encryption():
    """Test enhanced homomorphic encryption"""
    print("\n🔒 Testing Enhanced Homomorphic Encryption...")
    
    try:
        from backend.homomorphic_encryption_enhanced import EnhancedHomomorphicEncryption
        
        # Initialize with smaller key size for testing
        he = EnhancedHomomorphicEncryption(key_size=512)
        keypair = he.generate_keypair()
        
        # Test basic encryption/decryption
        plaintext = 42.5
        encrypted = he.encrypt(plaintext)
        decrypted = he.decrypt(encrypted)
        
        assert abs(decrypted - plaintext) < 0.1, f"Expected {plaintext}, got {decrypted}"
        print("✅ Basic encryption/decryption working")
        
        # Test homomorphic addition
        a = he.encrypt(10.0)
        b = he.encrypt(20.0)
        encrypted_sum = he.homomorphic_add(a, b)
        decrypted_sum = he.decrypt(encrypted_sum)
        
        assert abs(decrypted_sum - 30.0) < 0.1, f"Expected 30.0, got {decrypted_sum}"
        print("✅ Homomorphic addition working")
        
        return True
    except Exception as e:
        print(f"❌ Homomorphic encryption test error: {e}")
        traceback.print_exc()
        return False

def test_auth_utils():
    """Test authentication utilities"""
    print("\n🔑 Testing Authentication Utils...")
    
    try:
        from backend.auth_utils import get_password_hash, verify_password, create_access_token
        
        # Test password hashing
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed), "Password verification failed"
        assert not verify_password("wrongpassword", hashed), "Wrong password should not verify"
        print("✅ Password hashing and verification working")
        
        # Test token creation
        token = create_access_token(data={"sub": "test_user"})
        assert token is not None and len(token) > 0, "Token creation failed"
        print("✅ JWT token creation working")
        
        return True
    except Exception as e:
        print(f"❌ Auth utils test error: {e}")
        traceback.print_exc()
        return False

def test_data_encryption():
    """Test data encryption utilities"""
    print("\n🛡️ Testing Data Encryption...")
    
    try:
        from backend.encryption import encrypt_data, decrypt_data
        
        # Test data encryption
        test_data = "Sensitive health information"
        password = "encryption_password"
        
        encrypted = encrypt_data(test_data, password)
        decrypted = decrypt_data(encrypted, password)
        
        assert decrypted == test_data, f"Expected '{test_data}', got '{decrypted}'"
        print("✅ Data encryption/decryption working")
        
        return True
    except Exception as e:
        print(f"❌ Data encryption test error: {e}")
        traceback.print_exc()
        return False

def test_health_data_analysis():
    """Test health data analysis utilities"""
    print("\n📊 Testing Health Data Analysis...")
    
    try:
        from backend.utils import analyze_health_metrics, validate_csv_structure
        
        # Test health metrics analysis
        sample_data = {
            'blood_pressure_systolic': [120, 130, 125, 135],
            'blood_pressure_diastolic': [80, 85, 82, 88],
            'heart_rate': [70, 75, 72, 78]
        }
        
        analysis = analyze_health_metrics(sample_data)
        
        assert 'blood_pressure_systolic' in analysis, "Blood pressure analysis missing"
        assert 'statistics' in analysis['blood_pressure_systolic'], "Statistics missing"
        print("✅ Health data analysis working")
        
        return True
    except Exception as e:
        print(f"❌ Health data analysis test error: {e}")
        traceback.print_exc()
        return False

def test_configuration_files():
    """Test that all configuration files are present and valid"""
    print("\n⚙️ Testing Configuration Files...")
    
    try:
        # Check Docker files
        docker_files = [
            "Dockerfile.backend",
            "Dockerfile.frontend", 
            "docker-compose.yml"
        ]
        
        for file in docker_files:
            if not os.path.exists(file):
                print(f"❌ Missing Docker file: {file}")
                return False
        
        print("✅ Docker configuration files present")
        
        # Check CI/CD configuration
        if not os.path.exists(".github/workflows/ci-cd.yml"):
            print("❌ Missing CI/CD configuration")
            return False
        
        print("✅ CI/CD configuration present")
        
        # Check monitoring configuration
        monitoring_files = [
            "monitoring/prometheus.yml",
            "monitoring/alert_rules.yml",
            "monitoring/grafana/provisioning/datasources/prometheus.yml"
        ]
        
        for file in monitoring_files:
            if not os.path.exists(file):
                print(f"❌ Missing monitoring file: {file}")
                return False
        
        print("✅ Monitoring configuration files present")
        
        # Check environment template
        if not os.path.exists("env.template"):
            print("❌ Missing environment template")
            return False
        
        print("✅ Environment configuration present")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def test_documentation():
    """Test that all documentation is present"""
    print("\n📚 Testing Documentation...")
    
    try:
        docs = [
            "README_DEPLOYMENT.md",
            "docs/HIPAA_COMPLIANCE.md",
            "DEPLOYMENT.md"
        ]
        
        for doc in docs:
            if not os.path.exists(doc):
                print(f"❌ Missing documentation: {doc}")
                return False
        
        print("✅ All documentation present")
        return True
    except Exception as e:
        print(f"❌ Documentation test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Health Data Exchange Project Testing")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("SMPC Protocols", test_smpc_protocols),
        ("Homomorphic Encryption", test_homomorphic_encryption),
        ("Authentication Utils", test_auth_utils),
        ("Data Encryption", test_data_encryption),
        ("Health Data Analysis", test_health_data_analysis),
        ("Configuration Files", test_configuration_files),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project is ready for deployment.")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
