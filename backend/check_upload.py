from database import SessionLocal
from models import Upload
import json
import os
import sys
from pathlib import Path
from config import UPLOAD_DIR

def check_upload(upload_id):
    db = SessionLocal()
    try:
        upload = db.query(Upload).filter_by(id=upload_id).first()
        if not upload:
            print(f"\nNo upload found with ID {upload_id}")
            return
            
        print(f"\nUpload #{upload.id}:")
        print(f"Filename: {upload.filename}")
        print(f"Original Filename: {upload.original_filename}")
        print(f"Category: {upload.category}")
        print(f"Status: {upload.status}")
        print(f"Created At: {upload.created_at}")
        if upload.processed_at:
            print(f"Processed At: {upload.processed_at}")
        if upload.error_message:
            print(f"Error: {upload.error_message}")
        if upload.result:
            print("\nResult:")
            print(json.dumps(upload.result, indent=2))
        print("-" * 80)
            
    except Exception as e:
        print(f"Error checking upload: {e}")
    finally:
        db.close()

def check_upload_system():
    print("Checking upload system...")
    
    # Check if upload directory exists
    print(f"\nChecking upload directory: {UPLOAD_DIR}")
    if os.path.exists(UPLOAD_DIR):
        print("✓ Upload directory exists")
        
        # Check if it's writable
        try:
            test_file = os.path.join(UPLOAD_DIR, "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("✓ Upload directory is writable")
        except Exception as e:
            print(f"✗ Upload directory is not writable: {str(e)}")
            return False
    else:
        print("✗ Upload directory does not exist")
        try:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            print("✓ Created upload directory")
        except Exception as e:
            print(f"✗ Failed to create upload directory: {str(e)}")
            return False
    
    # Check database
    db_path = os.path.join(Path(__file__).resolve().parent, "health.db")
    print(f"\nChecking database: {db_path}")
    if os.path.exists(db_path):
        print("✓ Database file exists")
        if os.access(db_path, os.R_OK | os.W_OK):
            print("✓ Database file is readable and writable")
        else:
            print("✗ Database file permissions issue")
            return False
    else:
        print("✗ Database file does not exist")
        return False
    
    # Check test file
    test_file = os.path.join(Path(__file__).resolve().parent, "test_upload.csv")
    print(f"\nChecking test file: {test_file}")
    if os.path.exists(test_file):
        print("✓ Test file exists")
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                if 'date' in content and 'value' in content:
                    print("✓ Test file has valid content")
                else:
                    print("✗ Test file content may be invalid")
        except Exception as e:
            print(f"✗ Cannot read test file: {str(e)}")
            return False
    else:
        print("✗ Test file does not exist")
        return False
    
    return True

if __name__ == "__main__":
    if check_upload_system():
        print("\n✓ Upload system check passed")
        sys.exit(0)
    else:
        print("\n✗ Upload system check failed")
        sys.exit(1) 