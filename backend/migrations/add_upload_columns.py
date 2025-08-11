from sqlalchemy import create_engine, text
from config import DATABASE_URL, DATABASE_CONNECT_ARGS

def run_migration():
    # Create engine
    engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
    
    # Add columns if they don't exist
    with engine.connect() as connection:
        try:
            # Check if upload_path column exists
            result = connection.execute(text("SELECT upload_path FROM uploads LIMIT 1"))
        except Exception:
            print("Adding upload_path column...")
            connection.execute(text("ALTER TABLE uploads ADD COLUMN upload_path VARCHAR(500)"))
            connection.commit()
            print("Added upload_path column")

        try:
            # Check if checksum column exists
            result = connection.execute(text("SELECT checksum FROM uploads LIMIT 1"))
        except Exception:
            print("Adding checksum column...")
            connection.execute(text("ALTER TABLE uploads ADD COLUMN checksum VARCHAR(64)"))
            connection.commit()
            print("Added checksum column")

        # Update upload_path for existing records if it's NULL
        connection.execute(text("""
            UPDATE uploads 
            SET upload_path = CASE 
                WHEN org_id IS NOT NULL THEN org_id || '/' || filename 
                ELSE filename 
            END 
            WHERE upload_path IS NULL
        """))
        connection.commit()
        print("Updated upload paths for existing records")

if __name__ == "__main__":
    run_migration() 