#!/usr/bin/env python3
"""
Migration: Add security_method column to secure_computations table
Date: 2025-09-30
Description: Adds the missing security_method column to secure_computations table
"""

import sqlite3
import os
import sys

def add_security_method_column():
    """Add security_method column to secure_computations table"""

    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'health_data.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(secure_computations)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'security_method' in columns:
            print("Column 'security_method' already exists in secure_computations table")
            return True

        # Add the security_method column with default value 'homomorphic'
        cursor.execute("""
            ALTER TABLE secure_computations
            ADD COLUMN security_method TEXT DEFAULT 'homomorphic'
        """)

        conn.commit()
        print("Successfully added security_method column to secure_computations table")

        # Verify the column was added
        cursor.execute("PRAGMA table_info(secure_computations)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'security_method' in columns:
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
    print("Running migration: Add security_method column to secure_computations")
    print("=" * 60)

    success = add_security_method_column()

    if success:
        print("✓ Migration completed successfully")
        sys.exit(0)
    else:
        print("✗ Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
