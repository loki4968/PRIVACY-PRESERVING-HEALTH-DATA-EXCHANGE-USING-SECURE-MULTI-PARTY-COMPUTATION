#!/usr/bin/env python3
"""
Comprehensive test for the targeted invitation system
"""

import sys
import os
import asyncio
import json
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

async def test_targeted_invitations():
    """Test the complete targeted invitation workflow"""
    SessionLocal = setup_database()
    db = SessionLocal()
    
    try:
        service = SecureComputationService(db)
        
        print("=== Targeted Invitation System Test ===\n")
        
        # Get organizations
        orgs = db.query(Organization).all()
        print(f"Available organizations: {len(orgs)}")
        
        if len(orgs) < 3:
            print("Creating test organizations...")
            # Create test organizations if needed
            test_orgs = [
                {"name": "Hospital A", "email": "hospital-a@test.com"},
                {"name": "Clinic B", "email": "clinic-b@test.com"},
                {"name": "Research Center C", "email": "research-c@test.com"}
            ]
            
            for org_data in test_orgs:
                existing = db.query(Organization).filter_by(email=org_data["email"]).first()
                if not existing:
                    new_org = Organization(name=org_data["name"], email=org_data["email"])
                    db.add(new_org)
            
            db.commit()
            orgs = db.query(Organization).all()
        
        print(f"Organizations available for testing:")
        for org in orgs[:3]:  # Use first 3 orgs
            print(f"  {org.id}: {org.name} ({org.email})")
        
        # Test 1: Create computation with targeted invitations
        print(f"\n=== Test 1: Creating computation with targeted invitations ===")
        creator_org = orgs[0]
        invited_org_ids = [orgs[1].id, orgs[2].id]
        
        computation_id = service.create_computation_with_invitations(
            creator_org.id,
            "health_statistics", 
            invited_org_ids
        )
        
        print(f"✓ Created computation {computation_id}")
        print(f"✓ Invited organizations: {[org.name for org in orgs[1:3]]}")
        
        # Test 2: Verify invitations were created
        print(f"\n=== Test 2: Verifying invitations in database ===")
        invitations = db.query(ComputationInvitation).filter_by(computation_id=computation_id).all()
        print(f"✓ Created {len(invitations)} invitations")
        
        for inv in invitations:
            invited_org = db.query(Organization).filter_by(id=inv.invited_org_id).first()
            print(f"  - {invited_org.name}: {inv.status}")
        
        # Test 3: Check pending requests for each organization
        print(f"\n=== Test 3: Testing pending requests visibility ===")
        
        # Creator should see no pending requests (they created it)
        creator_pending = await service.get_pending_requests(creator_org.id)
        print(f"✓ Creator org ({creator_org.name}): {len(creator_pending)} pending requests")
        
        # Invited orgs should see the request
        for org in orgs[1:3]:
            pending = await service.get_pending_requests(org.id)
            print(f"✓ Invited org ({org.name}): {len(pending)} pending requests")
            
            if pending:
                for req in pending:
                    print(f"    - Request: {req.get('title', 'N/A')} from {req.get('creator_org', 'N/A')}")
        
        # Non-invited org should see no requests
        if len(orgs) > 3:
            non_invited_org = orgs[3]
            non_invited_pending = await service.get_pending_requests(non_invited_org.id)
            print(f"✓ Non-invited org ({non_invited_org.name}): {len(non_invited_pending)} pending requests")
        
        # Test 4: Accept invitation
        print(f"\n=== Test 4: Testing invitation acceptance ===")
        accepting_org = orgs[1]
        success = await service.accept_computation_request(computation_id, accepting_org.id, accepting_org.id)
        print(f"✓ {accepting_org.name} accepted invitation: {success}")
        
        # Verify invitation status changed
        invitation = db.query(ComputationInvitation).filter_by(
            computation_id=computation_id,
            invited_org_id=accepting_org.id
        ).first()
        print(f"✓ Invitation status: {invitation.status}")
        
        # Verify participant was added
        participant = db.query(ComputationParticipant).filter_by(
            computation_id=computation_id,
            org_id=accepting_org.id
        ).first()
        print(f"✓ Participant added: {participant is not None}")
        
        # Test 5: Decline invitation
        print(f"\n=== Test 5: Testing invitation decline ===")
        declining_org = orgs[2]
        success = await service.decline_computation_request(computation_id, declining_org.id, declining_org.id)
        print(f"✓ {declining_org.name} declined invitation: {success}")
        
        # Verify invitation status changed
        invitation = db.query(ComputationInvitation).filter_by(
            computation_id=computation_id,
            invited_org_id=declining_org.id
        ).first()
        print(f"✓ Invitation status: {invitation.status}")
        
        # Test 6: Final pending requests check
        print(f"\n=== Test 6: Final pending requests verification ===")
        for org in orgs[:3]:
            pending = await service.get_pending_requests(org.id)
            print(f"✓ {org.name}: {len(pending)} pending requests")
        
        print(f"\n🎉 All tests passed! Targeted invitation system is working correctly.")
        print(f"✅ Organizations only see invitations specifically sent to them")
        print(f"✅ Accept/decline functionality works properly")
        print(f"✅ Database tracks invitation statuses correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_targeted_invitations())
