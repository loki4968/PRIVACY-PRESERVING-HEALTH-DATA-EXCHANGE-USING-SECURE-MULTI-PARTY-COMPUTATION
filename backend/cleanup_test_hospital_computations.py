#!/usr/bin/env python3
"""
Cleanup script to remove computations created by a specific organization (e.g., "Test Hospital").

Usage:
  python cleanup_test_hospital_computations.py --org "Test Hospital" --dry-run
  python cleanup_test_hospital_computations.py --org "Test Hospital"

Notes:
- Deletes in FK-safe order: invitations -> results -> participants -> computation
- By default will actually delete; pass --dry-run to only print what would be deleted
- You can filter by status if desired (e.g., waiting_for_data, initialized, error)

Requires project virtualenv and DB access per backend/database.py
"""
import argparse
from typing import List

from database import SessionLocal
from models import SecureComputation, ComputationParticipant, ComputationResult, ComputationInvitation, Organization


def find_org_ids_by_name(db, org_name: str) -> List[int]:
    orgs = db.query(Organization).filter(Organization.name == org_name).all()
    return [o.id for o in orgs]


def delete_computation_tree(db, computation: SecureComputation, dry_run: bool = False) -> None:
    comp_id = computation.computation_id
    # 1. Invitations
    invitations = db.query(ComputationInvitation).filter_by(computation_id=comp_id).all()
    # 2. Results
    results = db.query(ComputationResult).filter_by(computation_id=comp_id).all()
    # 3. Participants
    participants = db.query(ComputationParticipant).filter_by(computation_id=comp_id).all()

    print(f"Computation {comp_id} ({computation.type}) - status={computation.status} | to delete: "
          f"{len(invitations)} invitations, {len(results)} results, {len(participants)} participants")

    if dry_run:
        return

    # Delete in safe order
    for inv in invitations:
        db.delete(inv)
    for res in results:
        db.delete(res)
    for part in participants:
        db.delete(part)

    # Finally delete computation
    db.delete(computation)


def main():
    parser = argparse.ArgumentParser(description="Remove computations created by a given organization")
    parser.add_argument("--org", required=True, help="Organization name, e.g., 'Test Hospital'")
    parser.add_argument("--status", nargs="*", default=None,
                        help="Optional statuses to filter by (e.g., waiting_for_data initialized error)")
    parser.add_argument("--dry-run", action="store_true", help="Only print actions, do not delete")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        org_ids = find_org_ids_by_name(db, args.org)
        if not org_ids:
            print(f"No organizations found with name '{args.org}'. Nothing to do.")
            return
        print(f"Found organizations with name '{args.org}': {org_ids}")

        q = db.query(SecureComputation).filter(SecureComputation.org_id.in_(org_ids))
        if args.status:
            q = q.filter(SecureComputation.status.in_(args.status))
        computations = q.all()

        if not computations:
            print("No computations matched filter. Nothing to delete.")
            return

        print(f"Matched {len(computations)} computation(s) for deletion.")
        for comp in computations:
            delete_computation_tree(db, comp, dry_run=args.dry_run)

        if args.dry_run:
            print("Dry-run complete. No changes committed.")
        else:
            db.commit()
            print("Deletion complete. Changes committed.")
    except Exception as e:
        db.rollback()
        print("Error during cleanup:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
