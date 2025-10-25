import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile
import shutil

from backend.main import app
from backend.models import Base, get_db
from backend.auth_utils import create_access_token

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test Hospital",
        "email": "test@hospital.com",
        "password": "testpassword123",
        "type": "hospital",
        "address": "123 Test St",
        "phone": "+1234567890",
        "license_number": "LIC123456"
    }

@pytest.fixture
def test_organization(db_session, test_user_data):
    """Create a test organization in the database."""
    from backend.models import Organization
    from backend.auth_utils import get_password_hash
    
    org = Organization(
        name=test_user_data["name"],
        email=test_user_data["email"],
        password_hash=get_password_hash(test_user_data["password"]),
        type=test_user_data["type"],
        address=test_user_data["address"],
        phone=test_user_data["phone"],
        license_number=test_user_data["license_number"],
        is_verified=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org

@pytest.fixture
def auth_headers(test_organization):
    """Create authentication headers for testing."""
    token = create_access_token(data={"sub": str(test_organization.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_csv_file(temp_upload_dir):
    """Create a sample CSV file for testing uploads."""
    csv_content = """patient_id,age,blood_pressure_systolic,blood_pressure_diastolic,blood_sugar,heart_rate
1,45,120,80,95,72
2,52,130,85,110,78
3,38,115,75,88,68
4,61,140,90,125,82
5,29,110,70,92,65"""
    
    file_path = os.path.join(temp_upload_dir, "test_health_data.csv")
    with open(file_path, "w") as f:
        f.write(csv_content)
    return file_path

@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        async def get(self, key):
            return self.data.get(key)
        
        async def set(self, key, value, ex=None):
            self.data[key] = value
        
        async def delete(self, key):
            self.data.pop(key, None)
        
        async def exists(self, key):
            return key in self.data
    
    return MockRedis()

@pytest.fixture
def mock_smtp():
    """Mock SMTP for testing email functionality."""
    class MockSMTP:
        def __init__(self):
            self.sent_emails = []
        
        def send_email(self, to_email, subject, body):
            self.sent_emails.append({
                "to": to_email,
                "subject": subject,
                "body": body
            })
            return True
    
    return MockSMTP()

# Test data fixtures
@pytest.fixture
def sample_health_metrics():
    """Sample health metrics data."""
    return {
        "blood_pressure": [120, 130, 115, 140, 110],
        "blood_sugar": [95, 110, 88, 125, 92],
        "heart_rate": [72, 78, 68, 82, 65],
        "age": [45, 52, 38, 61, 29]
    }

@pytest.fixture
def sample_computation_request():
    """Sample secure computation request."""
    return {
        "title": "Test Blood Pressure Analysis",
        "description": "Testing secure computation of blood pressure statistics",
        "computation_type": "statistics",
        "participants": ["test@hospital.com"],
        "parameters": {
            "metrics": ["blood_pressure_systolic", "blood_pressure_diastolic"],
            "operations": ["mean", "std", "count"]
        }
    }
