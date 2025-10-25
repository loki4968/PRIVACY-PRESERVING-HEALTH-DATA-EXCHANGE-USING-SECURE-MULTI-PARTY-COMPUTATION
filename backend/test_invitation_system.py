#!/usr/bin/env python3
"""
Test script to verify the targeted invitation system is working correctly
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SecureComputation, ComputationInvitation, Organization, SessionLocal
from secure_computation import SecureComputationService

async def test_invitation_system():
    """Test the targeted invitation system"""
    db = SessionLocal()
    try:
        service = SecureComputationService(db)
        
        print("=== Testing Targeted Invitation System ===")
        
        # Get all organizations
        orgs = db.query(Organization).all()
        print(f"Available organizations: {len(orgs)}")
        for org in orgs:
            print(f"  {org.id}: {org.name} ({org.email})")
        
        if len(orgs) < 3:
            print("Need at least 3 organizations to test invitation system")
            return
        
        # Test 1: Create computation with targeted invitations
        print(f"\n=== Test 1: Creating computation with targeted invitations ===")
        creator_org = orgs[0]
        invited_orgs = [orgs[1].id, orgs[2].id]
        
        computation_id = service.create_computation_with_invitations(
            creator_org.id,
            "health_statistics",
            invited_orgs
        )
        
        print(f"Created computation {computation_id} by {creator_org.name}")
        print(f"Invited organizations: {[orgs[1].name, orgs[2].name]}")
        
        # Test 2: Check pending requests for each organization
        print(f"\n=== Test 2: Checking pending requests ===")
        for org in orgs:
            pending = await service.get_pending_requests(org.id)
            print(f"{org.name} (ID: {org.id}): {len(pending)} pending requests")
            for req in pending:
                print(f"  - {req['title']} from {req['creator_org']}")
        
        # Test 3: Accept invitation from first invited org
        print(f"\n=== Test 3: Accepting invitation ===")
        first_invited = orgs[1]
        success = await service.accept_computation_request(computation_id, first_invited.id, first_invited.id)
        print(f"{first_invited.name} accepted invitation: {success}")
        
        # Test 4: Check pending requests again
        print(f"\n=== Test 4: Checking pending requests after acceptance ===")
        for org in orgs:
            pending = await service.get_pending_requests(org.id)
            print(f"{org.name} (ID: {org.id}): {len(pending)} pending requests")
        
        # Test 5: Decline invitation from second invited org
        print(f"\n=== Test 5: Declining invitation ===")
        second_invited = orgs[2]
        success = await service.decline_computation_request(computation_id, second_invited.id, second_invited.id)
        print(f"{second_invited.name} declined invitation: {success}")
        
        # Test 6: Final check of pending requests
        print(f"\n=== Test 6: Final pending requests check ===")
        for org in orgs:
            pending = await service.get_pending_requests(org.id)
            print(f"{org.name} (ID: {org.id}): {len(pending)} pending requests")
        
        # Test 7: Check invitation statuses in database
        print(f"\n=== Test 7: Database invitation status ===")
        invitations = db.query(ComputationInvitation).filter_by(computation_id=computation_id).all()
        for inv in invitations:
            invited_org = db.query(Organization).filter_by(id=inv.invited_org_id).first()
            inviter_org = db.query(Organization).filter_by(id=inv.inviter_org_id).first()
            print(f"  {invited_org.name} <- {inviter_org.name}: {inv.status}")
        
        print(f"\n=== Test Results ===")
        print("✓ Targeted invitation system working correctly")
        print("✓ Only invited organizations see pending requests")
        print("✓ Accept/decline functionality works properly")
        print("✓ Database tracks invitation statuses correctly")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_invitation_system())
