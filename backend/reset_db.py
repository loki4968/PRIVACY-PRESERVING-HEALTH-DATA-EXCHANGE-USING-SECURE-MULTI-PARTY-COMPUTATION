import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from backend.config import DATABASE_URL, DATABASE_CONNECT_ARGS
from backend.models import Base

def reset_database():
    print("Resetting database...")
    
    # Create engine
    engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("✓ Dropped all tables")
    
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Created all tables")
    
    # Clear upload directory
    from backend.config import UPLOAD_DIR
    if os.path.exists(UPLOAD_DIR):
        for root, dirs, files in os.walk(UPLOAD_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        print("✓ Cleared upload directory")
    
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database() 