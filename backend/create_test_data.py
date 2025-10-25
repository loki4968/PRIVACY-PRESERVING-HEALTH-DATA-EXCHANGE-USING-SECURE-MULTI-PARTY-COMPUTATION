#!/usr/bin/env python3
"""
Script to create test data for the Health Data Exchange Platform
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models import SessionLocal, Organization, OrgType
from auth_utils import hash_password, UserRole
from config import settings

def create_test_data():
    """Create test organizations for development"""
    db = SessionLocal()
    
    try:
        # Check if test data already exists
        existing_org = db.query(Organization).filter_by(email="test@hospital.com").first()
        if existing_org:
            print("✅ Test data already exists!")
            return
        
        # Create test organizations
        test_organizations = [
            {
                "name": "City General Hospital",
                "email": "test@hospital.com",
                "contact": "+1-555-0123",
                "type": OrgType.HOSPITAL,
                "location": "New York, NY",
                "password": "test123",
                "role": UserRole.DOCTOR
            },
            {
                "name": "Central Laboratory",
                "email": "test@lab.com",
                "contact": "+1-555-0456",
                "type": OrgType.LABORATORY,
                "location": "Boston, MA",
                "password": "test123",
                "role": UserRole.LAB_TECHNICIAN
            },
            {
                "name": "Community Pharmacy",
                "email": "test@pharmacy.com",
                "contact": "+1-555-0789",
                "type": OrgType.PHARMACY,
                "location": "Chicago, IL",
                "password": "test123",
                "role": UserRole.PHARMACIST
            }
        ]
        
        for org_data in test_organizations:
            hashed_password = hash_password(org_data["password"])
            
            org = Organization(
                name=org_data["name"],
                email=org_data["email"],
                contact=org_data["contact"],
                type=org_data["type"],
                location=org_data["location"],
                password_hash=hashed_password,
                role=org_data["role"],
                privacy_accepted=True,
                email_verified=True,
                is_active=True
            )
            
            db.add(org)
            print(f"✅ Created: {org_data['name']} ({org_data['email']})")
        
        db.commit()
        print("\n🎉 Test data created successfully!")
        print("\n📋 Test Login Credentials:")
        print("=" * 40)
        for org_data in test_organizations:
            print(f"Email: {org_data['email']}")
            print(f"Password: {org_data['password']}")
            print(f"Role: {org_data['role']}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating test data for Health Data Exchange Platform...")
    create_test_data()
