#!/usr/bin/env python3
"""
Migration: Add encryption_type column to computation_results table
Date: 2025-09-09
Description: Adds the missing encryption_type column to computation_results table
"""

import sqlite3
import os
import sys

def add_encryption_type_column():
    """Add encryption_type column to computation_results table"""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'health_data.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(computation_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'encryption_type' in columns:
            print("Column 'encryption_type' already exists in computation_results table")
            return True
        
        # Add the encryption_type column
        cursor.execute("""
            ALTER TABLE computation_results 
            ADD COLUMN encryption_type TEXT
        """)
        
        conn.commit()
        print("Successfully added encryption_type column to computation_results table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(computation_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'encryption_type' in columns:
            print("✓ Column verification successful")
            return True
        else:
            print("✗ Column verification failed")
            return False
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Run the migration"""
    print("Running migration: Add encryption_type column to computation_results")
    print("=" * 60)
    
    success = add_encryption_type_column()
    
    if success:
        print("✓ Migration completed successfully")
        sys.exit(0)
    else:
        print("✗ Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
