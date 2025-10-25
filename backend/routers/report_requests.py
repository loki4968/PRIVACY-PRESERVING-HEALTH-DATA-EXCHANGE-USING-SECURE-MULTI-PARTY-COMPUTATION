from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date
import os
import uuid
import shutil
from pydantic import BaseModel

from models import Organization, ReportRequest, ReportRequestStatus, UserRole, OrgType
from dependencies import get_db, get_current_user

router = APIRouter()

class OrganizationResponse(BaseModel):
    id: int
    name: str
    type: str

class ReportRequestCreate(BaseModel):
    organization_id: int
    visit_date: date
    description: Optional[str] = None

class ReportRequestUpdate(BaseModel):
    status: ReportRequestStatus
    rejection_reason: Optional[str] = None

class ReportRequestResponse(BaseModel):
    id: str
    organization_id: int
    organization_name: str
    visit_date: date
    description: Optional[str]
    status: ReportRequestStatus
    request_date: datetime
    response_date: Optional[datetime]
    rejection_reason: Optional[str]
    has_report: bool
    secret_code: Optional[str] = None

class SecretCodeVerification(BaseModel):
    secret_code: str

@router.get("/healthcare-organizations", response_model=List[OrganizationResponse])
async def get_healthcare_organizations(current_user: Organization = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only patients can view healthcare organizations
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view healthcare organizations"
        )
    
    # Get all healthcare organizations
    organizations = db.query(Organization).filter(Organization.role == UserRole.HEALTHCARE_PROVIDER).all()
    
    return [{
        "id": org.id,
        "name": org.name,
        "type": org.type.value if org.type else None
    } for org in organizations]

@router.post("/report-requests", response_model=ReportRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_report_request(request_data: ReportRequestCreate, current_user: Organization = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only patients can create report requests
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can create report requests"
        )
    
    # Check if organization exists
    organization = db.query(Organization).filter(
        Organization.id == request_data.organization_id,
        Organization.role == UserRole.HEALTHCARE_PROVIDER
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Healthcare organization not found"
        )
    
    # Create report request
    report_request = ReportRequest(
        patient_id=current_user.id,
        organization_id=request_data.organization_id,
        visit_date=request_data.visit_date,
        description=request_data.description
    )
    
    # Generate a secret code for the request
    report_request.generate_secret_code()
    
    db.add(report_request)
    db.commit()
    db.refresh(report_request)
    
    return {
        "id": report_request.id,
        "organization_id": organization.id,
        "organization_name": organization.name,
        "visit_date": report_request.visit_date,
        "description": report_request.description,
        "status": report_request.status,
        "request_date": report_request.request_date,
        "response_date": report_request.response_date,
        "rejection_reason": report_request.rejection_reason,
        "has_report": bool(report_request.report_file_path),
        "secret_code": report_request.secret_code
    }

@router.get("/report-requests", response_model=List[ReportRequestResponse])
async def get_report_requests(status: Optional[ReportRequestStatus] = None, current_user: Organization = Depends(get_current_user), db: Session = Depends(get_db)):
    # For patients, return their requests
    if current_user.role == UserRole.PATIENT:
        query = db.query(ReportRequest, Organization).join(
            Organization, ReportRequest.organization_id == Organization.id
        ).filter(ReportRequest.patient_id == current_user.id)
    # For healthcare providers, return requests directed to them
    else:
        query = db.query(ReportRequest, Organization).join(
            Organization, ReportRequest.patient_id == Organization.id
        ).filter(ReportRequest.organization_id == current_user.id)
    
    # Filter by status if provided
    if status:
        query = query.filter(ReportRequest.status == status)
    
    # Execute query and format results
    results = query.all()
    response = []
    
    for report_request, organization in results:
        response.append({
            "id": report_request.id,
            "organization_id": organization.id,
            "organization_name": organization.name,
            "visit_date": report_request.visit_date,
            "description": report_request.description,
            "status": report_request.status,
            "request_date": report_request.request_date,
            "response_date": report_request.response_date,
            "rejection_reason": report_request.rejection_reason,
            "has_report": bool(report_request.report_file_path),
            "secret_code": report_request.secret_code if current_user.role == UserRole.PATIENT else None
        })
    
    return response

@router.get("/report-requests/{request_id}", response_model=ReportRequestResponse)
async def get_report_request(request_id: str, current_user: Organization = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get the report request with organization info
    query = db.query(ReportRequest, Organization).join(
        Organization, ReportRequest.organization_id == Organization.id
    ).filter(ReportRequest.id == request_id)
    
    # Check if user has access to this request
    if current_user.role == UserRole.PATIENT:
        query = query.filter(ReportRequest.patient_id == current_user.id)
    else:
        query = query.filter(ReportRequest.organization_id == current_user.id)
    
    result = query.first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report request not found or you don't have access"
        )
    
    report_request, organization = result
    
    return {
        "id": report_request.id,
        "organization_id": organization.id,
        "organization_name": organization.name,
        "visit_date": report_request.visit_date,
        "description": report_request.description,
        "status": report_request.status,
        "request_date": report_request.request_date,
        "response_date": report_request.response_date,
        "rejection_reason": report_request.rejection_reason,
        "has_report": bool(report_request.report_file_path),
        "secret_code": report_request.secret_code if current_user.role == UserRole.PATIENT else None
    }

@router.put("/report-requests/{request_id}", response_model=ReportRequestResponse)
async def update_report_request(request_id: str, request_update: ReportRequestUpdate, current_user: Organization = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only healthcare providers can update report requests
    if current_user.role == UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can update report requests"
        )
    
    # Get the report request
    report_request = db.query(ReportRequest).filter(
        ReportRequest.id == request_id,
        ReportRequest.organization_id == current_user.id
    ).first()
    
    if not report_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report request not found or you don't have access"
        )
    
    # Update the report request
    report_request.status = request_update.status
    if request_update.status == ReportRequestStatus.REJECTED and request_update.rejection_reason:
        report_request.rejection_reason = request_update.rejection_reason
    
    report_request.response_date = datetime.utcnow()
    
    db.commit()
    db.refresh(report_request)
    
    # Get organization info for response
    organization = db.query(Organization).filter(Organization.id == report_request.organization_id).first()
    
    return {
        "id": report_request.id,
        "organization_id": organization.id,
        "organization_name": organization.name,
        "visit_date": report_request.visit_date,
        "description": report_request.description,
        "status": report_request.status,
        "request_date": report_request.request_date,
        "response_date": report_request.response_date,
        "rejection_reason": report_request.rejection_reason,
        "has_report": bool(report_request.report_file_path),
        "secret_code": None
    }

@router.post("/report-requests/{request_id}/upload", response_model=ReportRequestResponse)
async def upload_report(request_id: str, file: UploadFile = File(...), current_user: Organization = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only healthcare providers can upload reports
    if current_user.role == UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only healthcare providers can upload reports"
        )
    
    # Get the report request
    report_request = db.query(ReportRequest).filter(
        ReportRequest.id == request_id,
        ReportRequest.organization_id == current_user.id
    ).first()
    
    if not report_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report request not found or you don't have access"
        )
    
    # Ensure the request is approved
    if report_request.status != ReportRequestStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report request must be approved before uploading a report"
        )
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join("uploads", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(reports_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update the report request
    report_request.report_file_path = file_path
    report_request.response_date = datetime.utcnow()
    
    db.commit()
    db.refresh(report_request)
    
    # Get organization info for response
    organization = db.query(Organization).filter(Organization.id == report_request.organization_id).first()
    
    return {
        "id": report_request.id,
        "organization_id": organization.id,
        "organization_name": organization.name,
        "visit_date": report_request.visit_date,
        "description": report_request.description,
        "status": report_request.status,
        "request_date": report_request.request_date,
        "response_date": report_request.response_date,
        "rejection_reason": report_request.rejection_reason,
        "has_report": bool(report_request.report_file_path),
        "secret_code": None
    }

@router.get("/report-requests/{request_id}/download")
async def download_report(request_id: str, secret_code: Optional[str] = None, current_user: Organization = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get the report request
    query = db.query(ReportRequest)
    
    # Check if user has access to this request
    if current_user.role == UserRole.PATIENT:
        query = query.filter(ReportRequest.patient_id == current_user.id)
    else:
        query = query.filter(ReportRequest.organization_id == current_user.id)
    
    report_request = query.filter(ReportRequest.id == request_id).first()
    
    if not report_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report request not found or you don't have access"
        )
    
    # Check if report exists
    if not report_request.report_file_path or not os.path.exists(report_request.report_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Return the file
    return FileResponse(
        path=report_request.report_file_path,
        filename=os.path.basename(report_request.report_file_path),
        media_type="application/octet-stream"
    )

@router.post("/report-requests/access-by-code", response_model=ReportRequestResponse)
async def access_report_by_code(verification: SecretCodeVerification, db: Session = Depends(get_db)):
    # Find the report request by secret code
    report_request = db.query(ReportRequest).filter(
        ReportRequest.secret_code == verification.secret_code,
        ReportRequest.status == ReportRequestStatus.APPROVED,
        ReportRequest.report_file_path != None
    ).first()
    
    if not report_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No approved report found with this secret code"
        )
    
    # Get organization info for response
    organization = db.query(Organization).filter(Organization.id == report_request.organization_id).first()
    
    return {
        "id": report_request.id,
        "organization_id": organization.id,
        "organization_name": organization.name,
        "visit_date": report_request.visit_date,
        "description": report_request.description,
        "status": report_request.status,
        "request_date": report_request.request_date,
        "response_date": report_request.response_date,
        "rejection_reason": report_request.rejection_reason,
        "has_report": bool(report_request.report_file_path),
        "secret_code": report_request.secret_code
    }

@router.get("/report-requests/download-by-code/{secret_code}")
async def download_report_by_code(secret_code: str, db: Session = Depends(get_db)):
    # Find the report request by secret code
    report_request = db.query(ReportRequest).filter(
        ReportRequest.secret_code == secret_code,
        ReportRequest.status == ReportRequestStatus.APPROVED,
        ReportRequest.report_file_path != None
    ).first()
    
    if not report_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No approved report found with this secret code"
        )
    
    # Check if report exists
    if not os.path.exists(report_request.report_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Return the file
    return FileResponse(
        path=report_request.report_file_path,
        filename=os.path.basename(report_request.report_file_path),
        media_type="application/octet-stream"
    )