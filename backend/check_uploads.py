import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Upload, Organization
from config import DATABASE_CONNECT_ARGS

# Create engine and session with the correct database file
DATABASE_URL = "sqlite:///./health_data.db"
engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Get all uploads
    uploads = db.query(Upload).all()
    print("\nAll Uploads in Database:")
    print("-" * 80)
    if not uploads:
        print("No uploads found in the database")
    else:
        for upload in uploads:
            org = db.query(Organization).filter_by(id=upload.org_id).first()
            print(f"Upload ID: {upload.id}")
            print(f"Filename: {upload.filename}")
            print(f"Original Filename: {upload.original_filename}")
            print(f"Category: {upload.category}")
            print(f"Organization ID: {upload.org_id}")
            print(f"Organization Email: {org.email if org else 'N/A'}")
            print(f"Status: {upload.status}")
            print(f"Created At: {upload.created_at}")
            print(f"Processed At: {upload.processed_at}")
            print(f"File Size: {upload.file_size} bytes")
            
            # Show result summary
            if upload.result:
                try:
                    result_data = json.loads(upload.result) if isinstance(upload.result, str) else upload.result
                    print(f"Result Status: {result_data.get('status', 'N/A')}")
                    print(f"Analysis: {'Present' if result_data.get('analysis') else 'Empty'}")
                    
                    # Show file metadata if available
                    if 'file_metadata' in result_data:
                        metadata = result_data['file_metadata']
                        print(f"File Encoding: {metadata.get('encoding', 'N/A')}")
                        print(f"Row Count: {metadata.get('row_count', 'N/A')}")
                        print(f"Columns: {', '.join(metadata.get('columns', []))}")
                except Exception as e:
                    print(f"Error parsing result: {e}")
            else:
                print("No result data available")
                
            print("-" * 80)

    # Check upload directory
    import os
    from config import UPLOAD_DIR
    print("\nChecking Upload Directory:")
    print("-" * 80)
    if os.path.exists(UPLOAD_DIR):
        print(f"Upload directory exists: {UPLOAD_DIR}")
        for root, dirs, files in os.walk(UPLOAD_DIR):
            print(f"\nDirectory: {root}")
            if dirs:
                print("Subdirectories:", dirs)
            if files:
                print("Files:", files)
    else:
        print(f"Upload directory does not exist: {UPLOAD_DIR}")
        
finally:
    db.close()