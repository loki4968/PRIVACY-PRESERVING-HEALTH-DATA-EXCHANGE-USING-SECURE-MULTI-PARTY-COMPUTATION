#!/usr/bin/env python3
"""
Script to fix pending requests visibility issue by updating existing computations
to be visible to other organizations.
"""

import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SecureComputation, ComputationParticipant, Organization, SessionLocal
from secure_computation import SecureComputationService

async def fix_pending_requests():
    """Update existing computations to be visible to other organizations"""
    db = SessionLocal()
    try:
        service = SecureComputationService(db)
        
        print("=== Fixing Pending Requests Visibility ===")
        
        # Find all computations with "initialized" status that are recent (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        initialized_computations = db.query(SecureComputation).filter(
            SecureComputation.status == "initialized",
            SecureComputation.created_at > recent_date
        ).all()
        
        print(f"Found {len(initialized_computations)} initialized computations to update")
        
        updated_count = 0
        for comp in initialized_computations:
            # Check if this computation has any participants
            participants_count = db.query(ComputationParticipant).filter_by(
                computation_id=comp.computation_id
            ).count()
            
            # Get creator organization info
            creator_org = db.query(Organization).filter_by(id=comp.org_id).first()
            creator_name = creator_org.name if creator_org else f"Org {comp.org_id}"
            
            print(f"  Computation {comp.computation_id[:8]}... by {creator_name}")
            print(f"    Type: {comp.type}")
            print(f"    Created: {comp.created_at}")
            print(f"    Participants: {participants_count}")
            
            # Make computation public so other organizations can see it
            success = service.make_computation_public(comp.computation_id)
            if success:
                updated_count += 1
                print(f"    ✓ Updated to 'waiting_for_participants' status")
            else:
                print(f"    ✗ Failed to update")
        
        print(f"\n=== Summary ===")
        print(f"Updated {updated_count} out of {len(initialized_computations)} computations")
        
        # Now test the pending requests functionality
        print(f"\n=== Testing Pending Requests ===")
        
        # Get all organizations
        all_orgs = db.query(Organization).all()
        print(f"Found {len(all_orgs)} organizations:")
        
        for org in all_orgs:
            print(f"  {org.id}: {org.name} ({org.email}) - {org.type}")
            
            # Get pending requests for this organization
            pending_requests = await service.get_pending_requests(org.id)
            print(f"    Pending requests: {len(pending_requests)}")
            
            for req in pending_requests:
                print(f"      - {req['title']} from {req['creator_org']} (ID: {req['computation_id'][:8]}...)")
        
        print(f"\n=== Current Computations Status ===")
        all_computations = db.query(SecureComputation).order_by(SecureComputation.created_at.desc()).limit(10).all()
        for comp in all_computations:
            creator_org = db.query(Organization).filter_by(id=comp.org_id).first()
            participants_count = db.query(ComputationParticipant).filter_by(computation_id=comp.computation_id).count()
            print(f"  {comp.computation_id[:8]}... | {comp.status} | {comp.type} | Creator: {creator_org.name if creator_org else 'Unknown'} | Participants: {participants_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(fix_pending_requests())
