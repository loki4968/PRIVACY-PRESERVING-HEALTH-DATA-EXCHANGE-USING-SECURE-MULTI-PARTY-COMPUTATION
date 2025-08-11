from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Organization, Upload
from config import DATABASE_URL, DATABASE_CONNECT_ARGS

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Get all organizations
    orgs = db.query(Organization).all()
    print("\nOrganizations:")
    print("-" * 80)
    for org in orgs:
        print(f"ID: {org.id}")
        print(f"Email: {org.email}")
        print(f"Name: {org.name}")
        print(f"Type: {org.type}")
        print(f"Is Active: {org.is_active}")
        print(f"Email Verified: {org.email_verified}")
        print(f"Role: {org.role}")
        print("-" * 80)
        
    # Get all uploads with organization details
    print("\nUploads:")
    print("-" * 80)
    uploads = db.query(Upload).all()
    for upload in uploads:
        org = db.query(Organization).filter_by(id=upload.org_id).first()
        print(f"Upload ID: {upload.id}")
        print(f"Filename: {upload.filename}")
        print(f"Organization ID: {upload.org_id}")
        print(f"Organization Email: {org.email if org else 'N/A'}")
        print(f"Status: {upload.status}")
        print(f"Created At: {upload.created_at}")
        print("-" * 80)
        
finally:
    db.close() 