from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime
import uuid

class ReportRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReportRequest(Base):
    __tablename__ = "report_requests"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    visit_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReportRequestStatus), default=ReportRequestStatus.PENDING)
    request_date = Column(DateTime, default=datetime.utcnow)
    response_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    report_file_path = Column(String, nullable=True)
    secret_code = Column(String(8), nullable=True, index=True)
    
    # Relationships
    patient = relationship("Organization", foreign_keys=[patient_id])
    organization = relationship("Organization", foreign_keys=[organization_id])
    
    def generate_secret_code(self):
        """Generate a random 8-character alphanumeric secret code."""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        self.secret_code = ''.join(random.choice(chars) for _ in range(8))
        return self.secret_code

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)