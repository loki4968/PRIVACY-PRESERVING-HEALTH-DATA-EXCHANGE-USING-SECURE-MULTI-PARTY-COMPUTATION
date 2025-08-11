from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Organization
from config import DATABASE_URL, DATABASE_CONNECT_ARGS

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Get the organization
    org = db.query(Organization).filter_by(id=3).first()
    if org:
        print(f"Found organization: {org.email}")
        org.email_verified = True
        db.commit()
        print("Email verified successfully")
    else:
        print("Organization not found")
finally:
    db.close() 