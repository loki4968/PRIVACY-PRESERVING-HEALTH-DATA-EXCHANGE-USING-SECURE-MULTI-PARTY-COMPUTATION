#!/usr/bin/env python3
"""
Test script to verify that third organization can still see pending requests
after first two organizations accept their invitations
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

async def test_multiple_invitations_scenario():
    """Test the scenario where multiple organizations accept/decline invitations"""
    SessionLocal = setup_database()
    db = SessionLocal()
    
    try:
        service = SecureComputationService(db)
        
        print("=== Testing Multiple Invitations Scenario ===\n")
        
        # Get or create test organizations
        orgs = db.query(Organization).all()
        
        if len(orgs) < 4:
            print("Creating test organizations...")
            test_orgs = [
                {"name": "Hospital Alpha", "email": "alpha@test.com"},
                {"name": "Clinic Beta", "email": "beta@test.com"},
                {"name": "Research Gamma", "email": "gamma@test.com"},
                {"name": "Medical Delta", "email": "delta@test.com"}
            ]
            
            for org_data in test_orgs:
                existing = db.query(Organization).filter_by(email=org_data["email"]).first()
                if not existing:
                    new_org = Organization(name=org_data["name"], email=org_data["email"])
                    db.add(new_org)
            
            db.commit()
            orgs = db.query(Organization).all()
        
        # Use first 4 organizations for testing
        creator_org = orgs[0]
        org_1 = orgs[1]
        org_2 = orgs[2] 
        org_3 = orgs[3]
        
        print(f"Test Organizations:")
        print(f"  Creator: {creator_org.name} (ID: {creator_org.id})")
        print(f"  Invitee 1: {org_1.name} (ID: {org_1.id})")
        print(f"  Invitee 2: {org_2.name} (ID: {org_2.id})")
        print(f"  Invitee 3: {org_3.name} (ID: {org_3.id})")
        
        # Step 1: Create computation with 3 invitations
        print(f"\n=== Step 1: Creating computation with 3 invitations ===")
        invited_org_ids = [org_1.id, org_2.id, org_3.id]
        
        computation_id = service.create_computation_with_invitations(
            creator_org.id,
            "health_statistics",
            invited_org_ids
        )
        
        print(f"✓ Created computation {computation_id}")
        print(f"✓ Invited 3 organizations")
        
        # Step 2: Check all organizations can see the pending request
        print(f"\n=== Step 2: Initial pending requests check ===")
        for org in [org_1, org_2, org_3]:
            pending = await service.get_pending_requests(org.id)
            print(f"✓ {org.name}: {len(pending)} pending requests")
            assert len(pending) == 1, f"Expected 1 pending request for {org.name}, got {len(pending)}"
        
        # Step 3: First organization accepts
        print(f"\n=== Step 3: First organization accepts ===")
        success = await service.accept_computation_request(computation_id, org_1.id, org_1.id)
        print(f"✓ {org_1.name} accepted: {success}")
        
        # Check computation status
        computation = db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        print(f"✓ Computation status: {computation.status}")
        
        # Check remaining organizations can still see pending request
        print(f"Pending requests after first acceptance:")
        for org in [org_2, org_3]:
            pending = await service.get_pending_requests(org.id)
            print(f"  {org.name}: {len(pending)} pending requests")
            assert len(pending) == 1, f"Expected 1 pending request for {org.name} after first acceptance, got {len(pending)}"
        
        # Step 4: Second organization accepts
        print(f"\n=== Step 4: Second organization accepts ===")
        success = await service.accept_computation_request(computation_id, org_2.id, org_2.id)
        print(f"✓ {org_2.name} accepted: {success}")
        
        # Check computation status
        computation = db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        print(f"✓ Computation status: {computation.status}")
        
        # CRITICAL TEST: Third organization should still see the pending request
        print(f"Pending requests after second acceptance:")
        pending_org3 = await service.get_pending_requests(org_3.id)
        print(f"  {org_3.name}: {len(pending_org3)} pending requests")
        assert len(pending_org3) == 1, f"CRITICAL: Expected 1 pending request for {org_3.name} after second acceptance, got {len(pending_org3)}"
        
        # Step 5: Third organization accepts
        print(f"\n=== Step 5: Third organization accepts ===")
        success = await service.accept_computation_request(computation_id, org_3.id, org_3.id)
        print(f"✓ {org_3.name} accepted: {success}")
        
        # Check final computation status
        computation = db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        print(f"✓ Final computation status: {computation.status}")
        
        # Step 6: Verify no pending requests remain
        print(f"\n=== Step 6: Final verification ===")
        for org in [org_1, org_2, org_3]:
            pending = await service.get_pending_requests(org.id)
            print(f"✓ {org.name}: {len(pending)} pending requests")
            assert len(pending) == 0, f"Expected 0 pending requests for {org.name} after all accepted, got {len(pending)}"
        
        # Check invitation statuses
        invitations = db.query(ComputationInvitation).filter_by(computation_id=computation_id).all()
        print(f"✓ Invitation statuses:")
        for inv in invitations:
            invited_org = db.query(Organization).filter_by(id=inv.invited_org_id).first()
            print(f"  {invited_org.name}: {inv.status}")
            assert inv.status == 'accepted', f"Expected accepted status for {invited_org.name}, got {inv.status}"
        
        print(f"\n🎉 SUCCESS: All tests passed!")
        print(f"✅ Third organization could see pending request even after first two accepted")
        print(f"✅ Computation status properly managed throughout the process")
        print(f"✅ All invitations properly tracked and updated")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_multiple_invitations_scenario())
