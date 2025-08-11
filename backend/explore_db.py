import sqlite3
from pathlib import Path

def explore_database():
    # Get database path
    db_path = Path(__file__).resolve().parent / 'health.db'
    print(f"Database path: {db_path}")
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        return
        
    print(f"Database size: {db_path.stat().st_size / 1024:.2f} KB")
    
    # Connect to database
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("\nNo tables found in the database.")
            return
            
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"- {table[0]}")
            
        print("\nDetailed Table Information:")
        print("-" * 80)
        
        for table in tables:
            table_name = table[0]
            try:
                print(f"\nTable: {table_name}")
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print("\nColumns:")
                for col in columns:
                    col_id, name, type_, notnull, default, pk = col
                    print(f"  - {name} ({type_})", end="")
                    if pk: print(" [PRIMARY KEY]", end="")
                    if notnull: print(" [NOT NULL]", end="")
                    if default is not None: print(f" [DEFAULT: {default}]", end="")
                    print()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"\nTotal rows: {count}")
                
                if count > 0:
                    # Show first row as sample
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
                    sample = cursor.fetchone()
                    if sample:
                        print("\nSample row:")
                        for col, val in zip([c[1] for c in columns], sample):
                            print(f"  {col}: {val}")
                
                print("-" * 80)
                
            except sqlite3.Error as e:
                print(f"Error reading table {table_name}: {e}")
                continue
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    explore_database() 