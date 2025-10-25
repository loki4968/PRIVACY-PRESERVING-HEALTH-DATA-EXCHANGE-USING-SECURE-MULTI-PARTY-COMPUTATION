#!/usr/bin/env python3
"""
Script to list all users in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models import SessionLocal, Organization

def list_users():
    """List all users in the database"""
    db = SessionLocal()
    
    try:
        # Get all organizations
        organizations = db.query(Organization).all()
        
        if not organizations:
            print("❌ No organizations found in database!")
            return
        
        print(f"✅ Found {len(organizations)} organization(s) in database:")
        print("=" * 60)
        
        for org in organizations:
            print(f"ID: {org.id}")
            print(f"Name: {org.name}")
            print(f"Email: {org.email}")
            print(f"Role: {org.role}")
            print(f"Type: {org.type}")
            print(f"Active: {org.is_active}")
            print(f"Email Verified: {org.email_verified}")
            print("-" * 40)
        
        print("\n📋 Available Login Credentials:")
        print("=" * 40)
        for org in organizations:
            print(f"Email: {org.email}")
            print(f"Password: test123")
            print(f"Role: {org.role}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 Listing users in Health Data Exchange Platform...")
    list_users()
