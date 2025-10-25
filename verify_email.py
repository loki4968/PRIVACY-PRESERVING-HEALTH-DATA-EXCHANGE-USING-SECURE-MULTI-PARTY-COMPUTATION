import sys
sys.path.append('backend')
from backend.models import SessionLocal, Organization

db = SessionLocal()
org = db.query(Organization).filter(Organization.email == 'test@example.com').first()
if org:
    org.email_verified = True
    db.commit()
    print("Email verified for test@example.com")
else:
    print("Organization not found")
db.close()
