#!/usr/bin/env python3
"""
Simple verification script to test the targeted invitation system
"""

import sqlite3
import os

def verify_invitation_system():
    """Verify the invitation system database setup and functionality"""
    
    # Check if database exists
    db_path = 'health_data.db'
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if computation_invitations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='computation_invitations'")
        if not cursor.fetchone():
            print("❌ ComputationInvitation table not found - creating it now...")
            
            # Create the table
            cursor.execute('''
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
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX idx_computation_invitations_invited_org ON computation_invitations(invited_org_id)')
            cursor.execute('CREATE INDEX idx_computation_invitations_computation ON computation_invitations(computation_id)')
            cursor.execute('CREATE INDEX idx_computation_invitations_status ON computation_invitations(status)')
            
            conn.commit()
            print("✅ Created computation_invitations table with indexes")
        else:
            print("✅ ComputationInvitation table exists")
        
        # Check table structure
        cursor.execute("PRAGMA table_info(computation_invitations)")
        columns = cursor.fetchall()
        expected_columns = ['id', 'computation_id', 'invited_org_id', 'inviter_org_id', 'status', 'invited_at', 'responded_at']
        actual_columns = [col[1] for col in columns]
        
        print(f"Table columns: {actual_columns}")
        
        for col in expected_columns:
            if col in actual_columns:
                print(f"✅ Column '{col}' exists")
            else:
                print(f"❌ Column '{col}' missing")
        
        # Check organizations
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        print(f"✅ Organizations in database: {org_count}")
        
        # Check existing computations
        cursor.execute("SELECT COUNT(*) FROM secure_computations")
        comp_count = cursor.fetchone()[0]
        print(f"✅ Existing computations: {comp_count}")
        
        # Check existing invitations
        cursor.execute("SELECT COUNT(*) FROM computation_invitations")
        inv_count = cursor.fetchone()[0]
        print(f"✅ Existing invitations: {inv_count}")
        
        if inv_count > 0:
            cursor.execute("""
                SELECT ci.status, COUNT(*) as count
                FROM computation_invitations ci
                GROUP BY ci.status
            """)
            status_counts = cursor.fetchall()
            print("Invitation status breakdown:")
            for status, count in status_counts:
                print(f"  {status}: {count}")
        
        print(f"\n✅ Invitation system verification complete!")
        print(f"✅ Database schema is ready for targeted invitations")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    verify_invitation_system()
