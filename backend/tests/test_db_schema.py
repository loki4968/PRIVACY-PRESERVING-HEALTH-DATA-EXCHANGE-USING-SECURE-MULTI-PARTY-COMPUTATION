import os
import tempfile
from datetime import datetime, timedelta
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from database import Base
from main import app, get_db
from models import ReportRequest, ReportRequestStatus, Organization, OrgType
from auth_utils import UserRole

# Create an in-memory SQLite test database
SQLITE_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import all models to ensure they're registered with Base.metadata
from models import *

# Create the database tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Get the inspector to check tables
inspector = inspect(engine)
print("Tables created:", inspector.get_table_names())

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

def test_report_request_schema():
    """Test that the ReportRequest model has the secret_code column."""
    # Get the inspector
    inspector = inspect(engine)
    
    # Check if the report_requests table exists
    assert "report_requests" in inspector.get_table_names(), "report_requests table does not exist"
    
    # Get the columns of the report_requests table
    columns = inspector.get_columns("report_requests")
    column_names = [col["name"] for col in columns]
    
    # Print all columns for debugging
    print("\nColumns in report_requests table:")
    for col in columns:
        print(f"  {col['name']} ({col['type']})")
    
    # Check if the secret_code column exists
    assert "secret_code" in column_names, "secret_code column does not exist in report_requests table"
    
    # Create a session
    db = TestingSessionLocal()
    
    try:
        # Create a test organization
        org = Organization(
            name="Test Hospital",
            email="test@hospital.com",
            password_hash="hashed_password",
            type=OrgType.HOSPITAL,
            role=UserRole.DOCTOR,
            contact="123-456-7890",
            location="Test Location",
            privacy_accepted=True,
            email_verified=True
        )
        
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create a test report request with a secret code
        request = ReportRequest(
            patient_id=org.id,
            organization_id=org.id,
            visit_date=datetime.now() - timedelta(days=7),
            description="Test report request",
            status=ReportRequestStatus.APPROVED,
            request_date=datetime.now(),
            secret_code="ABCD1234"  # Manually set a secret code
        )
        
        db.add(request)
        db.commit()
        db.refresh(request)
        
        # Verify the secret code was saved
        saved_request = db.query(ReportRequest).filter(ReportRequest.id == request.id).first()
        assert saved_request is not None, "Report request not found"
        assert saved_request.secret_code == "ABCD1234", "Secret code not saved correctly"
        
        # Test the API endpoint
        response = client.post(
            "/api/report-requests/access-by-code",
            json={"secret_code": "ABCD1234"}
        )
        
        # Print response for debugging
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.json() if response.status_code != 500 else response.text}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        data = response.json()
        assert data["id"] == request.id, "Report request ID does not match"
        assert data["secret_code"] == "ABCD1234", "Secret code does not match"
        
    finally:
        # Clean up
        db.query(ReportRequest).delete()
        db.query(Organization).delete()
        db.commit()
        db.close()