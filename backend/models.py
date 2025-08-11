from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, LargeBinary, Enum, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from backend.encryption_utils import EncryptionManager, validate_health_data, sanitize_health_data
from backend.auth_utils import UserRole
from backend.config import DATABASE_URL, DATABASE_CONNECT_ARGS
import enum
import json
import os

# Database setup
engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OrgType(str, enum.Enum):
    HOSPITAL = "HOSPITAL"
    CLINIC = "CLINIC"
    LABORATORY = "LABORATORY"
    PHARMACY = "PHARMACY"
    PATIENT = "PATIENT"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    contact = Column(String(50), nullable=False)
    type = Column(Enum(OrgType), nullable=False)
    location = Column(String(200), nullable=False)
    privacy_accepted = Column(Boolean, nullable=False, default=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PATIENT)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(32))
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login = Column(DateTime)
    account_locked_until = Column(DateTime)
    password_changed_at = Column(DateTime)
    last_password_reset = Column(DateTime)
    session_tokens = Column(JSON, default=list)  # Store refresh tokens

    uploads = relationship("Upload", back_populates="organization", cascade="all, delete-orphan")
    health_records = relationship("SecureHealthRecord", back_populates="organization", cascade="all, delete-orphan")
    computation_results = relationship("SecureComputationResult", back_populates="organization", cascade="all, delete-orphan")

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String(100), nullable=False)
    result = Column(JSON)
    status = Column(String(20), default="pending", nullable=False)  # pending, processing, completed, error
    error_message = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)

    organization = relationship("Organization", back_populates="uploads")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "has_error": bool(self.error_message),
            "error_message": self.error_message,
            "file_size": self.file_size,
            "result": self.result,
            "org_id": self.org_id
        }

    def get_file_path(self):
        """Get the absolute path to the uploaded file."""
        return os.path.join(UPLOAD_DIR, str(self.org_id), self.filename)

    def verify_file(self):
        """Verify the uploaded file exists and matches the stored checksum."""
        file_path = self.get_file_path()
        if not file_path or not os.path.exists(file_path):
            return False
        if not self.checksum:
            return True  # Skip verification if no checksum stored
        current_hash = hash_file_content(file_path)
        return current_hash == self.checksum

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("Organization")

class SecureHealthRecord(Base):
    __tablename__ = "secure_health_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    data_type = Column(String)
    encrypted_value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="health_records")
    
    def encrypt_value(self, value: str):
        """Encrypt the health record value"""
        encryption_manager = EncryptionManager()
        self.encrypted_value = encryption_manager.encrypt(value)

    def decrypt_value(self) -> str:
        """Decrypt the health record value"""
        encryption_manager = EncryptionManager()
        return encryption_manager.decrypt(self.encrypted_value)

    def set_data(self, data: dict):
        """Set and encrypt the health record data"""
        # Validate the data
        if not validate_health_data(data):
            raise ValueError("Invalid health data format")
        
        # Sanitize the data
        sanitized_data = sanitize_health_data(data)
        
        # Convert to string for encryption
        data_str = json.dumps(sanitized_data)
        
        # Encrypt the data
        self.encrypt_value(data_str)

    def get_data(self) -> dict:
        """Get and decrypt the health record data"""
        if not self.encrypted_value:
            return None
        
        # Decrypt the data
        decrypted_str = self.decrypt_value()
        
        # Parse JSON string back to dictionary
        try:
            return json.loads(decrypted_str)
        except json.JSONDecodeError:
            raise ValueError("Failed to decode health record data")

class SecureComputation(Base):
    __tablename__ = 'secure_computations'

    id = Column(Integer, primary_key=True)
    computation_id = Column(String, unique=True, nullable=False)
    org_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    result = Column(JSON)
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    participants = relationship("ComputationParticipant", back_populates="computation")
    results = relationship("ComputationResult", back_populates="computation")

class ComputationParticipant(Base):
    __tablename__ = 'computation_participants'

    id = Column(Integer, primary_key=True)
    computation_id = Column(String, ForeignKey('secure_computations.computation_id'), nullable=False)
    org_id = Column(Integer, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    computation = relationship("SecureComputation", back_populates="participants")

class ComputationResult(Base):
    __tablename__ = 'computation_results'

    id = Column(Integer, primary_key=True)
    computation_id = Column(String, ForeignKey('secure_computations.computation_id'), nullable=False)
    org_id = Column(Integer, nullable=False)
    data_points = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    computation = relationship("SecureComputation", back_populates="results")

class SecureComputationResult(Base):
    __tablename__ = "secure_computation_results"

    id = Column(Integer, primary_key=True, index=True)
    computation_id = Column(String, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    computation_type = Column(String)
    encrypted_result = Column(LargeBinary)
    result_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="computation_results")
    
    def __init__(self, **kwargs):
        self.encryption_manager = EncryptionManager()
        super().__init__(**kwargs)
    
    def set_result(self, result: dict):
        """Encrypt and store computation result."""
        self.encrypted_result, _ = self.encryption_manager.encrypt_data(result)
    
    def get_result(self) -> dict:
        """Decrypt and retrieve computation result."""
        if not self.encrypted_result:
            return None
        return self.encryption_manager.decrypt_data(self.encrypted_result) 