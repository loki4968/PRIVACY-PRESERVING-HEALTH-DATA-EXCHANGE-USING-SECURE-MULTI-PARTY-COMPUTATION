#!/usr/bin/env python3
"""
Test script to verify if multiple organizations can accept the same computation request
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import SecureComputation, ComputationInvitation, Organization, ComputationParticipant
from secure_computation import SecureComputationService
from config import DATABASE_URL, DATABASE_CONNECT_ARGS

def setup_database():
    """Setup database connection and ensure tables exist"""
    engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    from models import Base
    Base.metadata.create_all(bind=engine)
    
    return SessionLocal

async def test_multiple_acceptance():
    """Test if multiple organizations can accept the same computation request"""
    SessionLocal = setup_database()
    db = SessionLocal()
    
    try:
        service = SecureComputationService(db)
        
        print("=== Testing Multiple Organizations Accepting Same Request ===\n")
        
        # Get or create test organizations
        orgs = db.query(Organization).all()
        
        if len(orgs) < 4:
            print("Creating test organizations...")
            test_orgs = [
                {"name": "Creator Org", "email": "creator@test.com"},
                {"name": "Org Alpha", "email": "alpha@test.com"},
                {"name": "Org Beta", "email": "beta@test.com"},
                {"name": "Org Gamma", "email": "gamma@test.com"}
            ]
            
            for org_data in test_orgs:
                existing = db.query(Organization).filter_by(email=org_data["email"]).first()
                if not existing:
                    new_org = Organization(name=org_data["name"], email=org_data["email"])
                    db.add(new_org)
            
            db.commit()
            orgs = db.query(Organization).all()
        
        # Use first 4 organizations
        creator_org = orgs[0]
        org_alpha = orgs[1]
        org_beta = orgs[2]
        org_gamma = orgs[3]
        
        print(f"Test Organizations:")
        print(f"  Creator: {creator_org.name} (ID: {creator_org.id})")
        print(f"  Alpha: {org_alpha.name} (ID: {org_alpha.id})")
        print(f"  Beta: {org_beta.name} (ID: {org_beta.id})")
        print(f"  Gamma: {org_gamma.name} (ID: {org_gamma.id})")
        
        # Step 1: Create computation with invitations to 3 organizations
        print(f"\n=== Step 1: Creating computation with 3 invitations ===")
        invited_org_ids = [org_alpha.id, org_beta.id, org_gamma.id]
        
        computation_id = service.create_computation_with_invitations(
            creator_org.id,
            "health_statistics",
            invited_org_ids
        )
        
        print(f"✓ Created computation {computation_id}")
        print(f"✓ Invited 3 organizations")
        
        # Step 2: Check all organizations can see the pending request
        print(f"\n=== Step 2: Verifying all organizations see pending request ===")
        for org in [org_alpha, org_beta, org_gamma]:
            pending = await service.get_pending_requests(org.id)
            print(f"✓ {org.name}: {len(pending)} pending requests")
            if len(pending) != 1:
                print(f"❌ ERROR: Expected 1 pending request for {org.name}, got {len(pending)}")
                return False
        
        # Step 3: Alpha accepts
        print(f"\n=== Step 3: Alpha accepts ===")
        alpha_success = await service.accept_computation_request(computation_id, org_alpha.id, org_alpha.id)
        print(f"✓ Alpha acceptance: {alpha_success}")
        
        if not alpha_success:
            print("❌ ERROR: Alpha should be able to accept")
            return False
        
        # Check participants
        participants = db.query(ComputationParticipant).filter_by(computation_id=computation_id).count()
        print(f"✓ Participants after Alpha: {participants}")
        
        # Step 4: Beta accepts
        print(f"\n=== Step 4: Beta accepts ===")
        beta_success = await service.accept_computation_request(computation_id, org_beta.id, org_beta.id)
        print(f"✓ Beta acceptance: {beta_success}")
        
        if not beta_success:
            print("❌ ERROR: Beta should be able to accept")
            return False
        
        # Check participants
        participants = db.query(ComputationParticipant).filter_by(computation_id=computation_id).count()
        print(f"✓ Participants after Beta: {participants}")
        
        # Step 5: Gamma accepts
        print(f"\n=== Step 5: Gamma accepts ===")
        gamma_success = await service.accept_computation_request(computation_id, org_gamma.id, org_gamma.id)
        print(f"✓ Gamma acceptance: {gamma_success}")
        
        if not gamma_success:
            print("❌ ERROR: Gamma should be able to accept")
            return False
        
        # Check final participants
        participants = db.query(ComputationParticipant).filter_by(computation_id=computation_id).count()
        print(f"✓ Final participants: {participants}")
        
        # Step 6: Verify all invitations are accepted
        print(f"\n=== Step 6: Verifying invitation statuses ===")
        invitations = db.query(ComputationInvitation).filter_by(computation_id=computation_id).all()
        accepted_count = 0
        
        for inv in invitations:
            invited_org = db.query(Organization).filter_by(id=inv.invited_org_id).first()
            print(f"✓ {invited_org.name}: {inv.status}")
            if inv.status == 'accepted':
                accepted_count += 1
        
        # Step 7: Check computation status
        computation = db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        print(f"\n=== Step 7: Final computation status ===")
        print(f"✓ Computation status: {computation.status}")
        print(f"✓ Total organizations: {participants + 1} (including creator)")
        print(f"✓ Accepted invitations: {accepted_count}")
        
        # Final verification
        if participants == 3 and accepted_count == 3:
            print(f"\n🎉 SUCCESS: Multiple organizations CAN accept the same request!")
            print(f"✅ All 3 invited organizations successfully accepted")
            print(f"✅ Total of 4 organizations in computation (creator + 3 participants)")
            return True
        else:
            print(f"\n❌ ISSUE: Not all organizations could accept")
            print(f"Expected 3 participants, got {participants}")
            print(f"Expected 3 accepted invitations, got {accepted_count}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_multiple_acceptance())
