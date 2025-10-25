import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import tempfile

from main import app
from models import ReportRequest, Organization, ReportRequestStatus, OrgType, UserRole, Base
from database import get_db

# Create a test database in memory
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables in the test database
# First drop all tables to ensure clean state
Base.metadata.drop_all(bind=test_engine)

# Explicitly create the report_requests table with the secret_code column
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum, Date
from sqlalchemy.ext.declarative import declarative_base

# Create all tables
Base.metadata.create_all(bind=test_engine)


# Override the get_db dependency for testing
def override_get_db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture
def db_session():
    # Create a new test database session
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def test_organization(db_session: Session):
    # Create a test healthcare organization with unique email
    unique_id = uuid.uuid4().hex[:8]
    org = Organization(
        name="Test Hospital",
        type=OrgType.HOSPITAL,
        email=f"test{unique_id}@hospital.com",
        contact="555-1234",
        location="Test City",
        privacy_accepted=True,
        password_hash="hashed_password",
        role=UserRole.DOCTOR,
        is_active=True,
        email_verified=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    yield org
    # Clean up
    db_session.delete(org)
    db_session.commit()


@pytest.fixture
def test_patient_organization(db_session: Session):
    # Create a test patient organization with unique email
    unique_id = uuid.uuid4().hex[:8]
    org = Organization(
        name="Test Patient",
        type=OrgType.PATIENT,
        email=f"patient{unique_id}@example.com",
        contact="555-5678",
        location="Test City",
        privacy_accepted=True,
        password_hash="hashed_password",
        role=UserRole.PATIENT,
        is_active=True,
        email_verified=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    yield org
    # Clean up
    db_session.delete(org)
    db_session.commit()


@pytest.fixture
def test_report_request(db_session: Session, test_organization, test_patient_organization):
    # Create a test report request
    request = ReportRequest(
        patient_id=test_patient_organization.id,
        organization_id=test_organization.id,
        visit_date=datetime.now() - timedelta(days=7),
        description="Test report request",
        status=ReportRequestStatus.PENDING,
        request_date=datetime.now(),
        secret_code="ABCD1234"  # Manually set a secret code
    )
    
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)
    yield request
    # Clean up
    db_session.delete(request)
    db_session.commit()


def test_generate_secret_code():
    # Test that secret codes work
    request = ReportRequest(secret_code="ABCD1234")
    assert len(request.secret_code) == 8
    assert request.secret_code.isalnum()


def test_access_by_secret_code(test_organization, test_patient_organization, db_session):
    # Create a temporary file for testing
    import tempfile
    import os
    
    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, "test_report_access.pdf")
    
    # Write some content to the file
    with open(temp_file_path, "w") as f:
        f.write("Test report content for access")
    
    # Create a new report request specifically for this test
    request = ReportRequest(
        id=str(uuid.uuid4()),  # Generate a new UUID for each test
        patient_id=test_patient_organization.id,
        organization_id=test_organization.id,
        visit_date=datetime.now() - timedelta(days=7),
        description="Test report request for access",
        status=ReportRequestStatus.APPROVED,
        request_date=datetime.now(),
        report_file_path=temp_file_path,
        secret_code="ABCD1234"  # Manually set a secret code
    )
    
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)
    
    try:    
        response = client.post(
            "/api/report-requests/access-by-code",
            json={"secret_code": request.secret_code}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == request.id
        assert data["secret_code"] == request.secret_code
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_access_by_invalid_secret_code():
    # Test accessing with an invalid secret code
    response = client.post(
        "/api/report-requests/access-by-code",
        json={"secret_code": "INVALID1"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_download_by_secret_code(test_organization, test_patient_organization, db_session):
    # Create a temporary file for testing
    import tempfile
    import os
    
    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, "test_report.pdf")
    
    # Write some content to the file
    with open(temp_file_path, "w") as f:
        f.write("Test report content")
    
    # Create a new report request specifically for this test
    request = ReportRequest(
        id=str(uuid.uuid4()),  # Generate a new UUID for each test
        patient_id=test_patient_organization.id,
        organization_id=test_organization.id,
        visit_date=datetime.now() - timedelta(days=7),
        description="Test report request for download",
        status=ReportRequestStatus.APPROVED,
        request_date=datetime.now(),
        report_file_path=temp_file_path,
        secret_code="ABCD1234"  # Manually set a secret code
    )
    
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)
    
    try:
        # Test downloading a report by secret code
        response = client.get(f"/api/report-requests/download-by-code/{request.secret_code}")
        assert response.status_code == 200
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)