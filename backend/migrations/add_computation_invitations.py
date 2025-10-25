#!/usr/bin/env python3
"""
Migration script to add ComputationInvitation table for targeted invitations
"""

import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATABASE_URL, DATABASE_CONNECT_ARGS

def run_migration():
    """Add ComputationInvitation table to support targeted invitations"""
    engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
    
    try:
        with engine.connect() as conn:
            # Check if table already exists
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='computation_invitations'
            """))
            
            if result.fetchone():
                print("ComputationInvitation table already exists")
                return
            
            # Create the computation_invitations table
            conn.execute(text("""
                CREATE TABLE computation_invitations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    computation_id VARCHAR NOT NULL,
                    invited_org_id INTEGER NOT NULL,
                    inviter_org_id INTEGER NOT NULL,
                    status VARCHAR DEFAULT 'pending' NOT NULL,
                    invited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    responded_at DATETIME,
                    FOREIGN KEY (computation_id) REFERENCES secure_computations(computation_id),
                    FOREIGN KEY (invited_org_id) REFERENCES organizations(id),
                    FOREIGN KEY (inviter_org_id) REFERENCES organizations(id)
                )
            """))
            
            # Create indexes for better performance
            conn.execute(text("""
                CREATE INDEX idx_computation_invitations_invited_org 
                ON computation_invitations(invited_org_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_computation_invitations_computation 
                ON computation_invitations(computation_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX idx_computation_invitations_status 
                ON computation_invitations(status)
            """))
            
            conn.commit()
            print("✓ Created computation_invitations table with indexes")
            
            # Migrate existing computations to invitation-based system
            # For now, we'll leave existing computations as they are
            # New computations will use the invitation system
            
            print("✓ Migration completed successfully")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        raise e

if __name__ == "__main__":
    run_migration()
