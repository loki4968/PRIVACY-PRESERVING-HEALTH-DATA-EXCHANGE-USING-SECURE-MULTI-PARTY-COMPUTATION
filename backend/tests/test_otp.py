#!/usr/bin/env python3
"""
Test OTP functionality without email configuration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from otp_utils import generate_otp, verify_otp, otp_store

def test_otp_system():
    """Test the OTP system"""
    print("🔍 Testing OTP System...")
    print("=" * 50)
    
    # Test email
    test_email = "test@example.com"
    
    # Generate OTP
    print(f"📧 Generating OTP for: {test_email}")
    otp = generate_otp(test_email)
    print(f"✅ Generated OTP: {otp}")
    
    # Check if OTP is stored
    if test_email in otp_store:
        stored_data = otp_store[test_email]
        print(f"✅ OTP stored: {stored_data['otp']}")
        print(f"📅 Timestamp: {stored_data['timestamp']}")
        print(f"🔄 Attempts: {stored_data['attempts']}")
    else:
        print("❌ OTP not stored!")
        return
    
    # Test verification with correct OTP
    print(f"\n🔐 Testing verification with correct OTP: {otp}")
    result = verify_otp(test_email, otp)
    print(f"✅ Verification result: {result}")
    
    # Test verification with wrong OTP
    print(f"\n🔐 Testing verification with wrong OTP: 123456")
    result = verify_otp(test_email, "123456")
    print(f"❌ Verification result: {result}")
    
    # Check if OTP is cleared after successful verification
    if test_email not in otp_store:
        print("✅ OTP cleared after successful verification")
    else:
        print("❌ OTP not cleared after verification")

def test_email_sending():
    """Test email sending functionality"""
    print("\n📧 Testing Email Sending...")
    print("=" * 50)
    
    try:
        from otp_utils import send_otp_email
        test_email = "test@example.com"
        test_otp = "123456"
        
        print(f"📧 Attempting to send OTP to: {test_email}")
        result = send_otp_email(test_email, test_otp)
        print(f"📧 Email sending result: {result}")
        
        if not result:
            print("⚠️  Email sending failed - this is expected without proper SMTP configuration")
            print("💡 For testing, you can:")
            print("   1. Configure SMTP settings in .env file")
            print("   2. Use a test email service")
            print("   3. Check the console for the OTP instead")
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        print("💡 This is expected without proper email configuration")

if __name__ == "__main__":
    test_otp_system()
    test_email_sending()
