#!/usr/bin/env python3
"""
Script to verify user email
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models import SessionLocal, Organization

def verify_user_email(email):
    """Verify user email"""
    db = SessionLocal()
    
    try:
        # Find the user
        user = db.query(Organization).filter_by(email=email).first()
        
        if not user:
            print(f"❌ User with email {email} not found!")
            return
        
        print(f"✅ Found user: {user.name} ({user.email})")
        print(f"Current email verified: {user.email_verified}")
        
        # Verify the email
        user.email_verified = True
        user.is_active = True
        db.commit()
        
        print(f"✅ Email verified successfully!")
        print(f"New email verified status: {user.email_verified}")
        
    except Exception as e:
        print(f"❌ Error verifying email: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    email = "lokichowdaryt@gmail.com"
    print(f"🔧 Verifying email for: {email}")
    verify_user_email(email)
