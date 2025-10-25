"""
Migration to add status column to computation_participants table
"""
import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add status column to computation_participants table"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'health_data.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if status column already exists
        cursor.execute("PRAGMA table_info(computation_participants)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            # Add status column with default value
            cursor.execute("""
                ALTER TABLE computation_participants 
                ADD COLUMN status TEXT NOT NULL DEFAULT 'active'
            """)
            
            print(f"Added status column to computation_participants table at {datetime.now()}")
        else:
            print("Status column already exists in computation_participants table")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("Migration completed successfully")
    else:
        print("Migration failed")
