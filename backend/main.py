from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.models import (
    Base, 
    engine, 
    SessionLocal, 
    get_db,
    Organization,
    Upload,
    OrgType,
    SecureHealthRecord,
    SecureComputation,
    ComputationParticipant,
    ComputationResult
)
from backend.utils import run_analysis, allowed_file_extension, validate_file_size
from backend.auth_utils import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_access_token, UserRole, Permission, get_user_permissions
)
from backend.dependencies import get_current_user, require_permissions
from datetime import datetime, timedelta
from backend.config import UPLOAD_DIR
import shutil
import os
import mimetypes
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from backend.otp_utils import generate_otp, verify_otp, send_otp_email
import re
import dns.resolver
from backend.secure_computation import SecureComputationService, SecureHealthMetricsComputation
import uuid
import json
from backend.routers import auth, secure_computations, analytics
from backend.websocket import metrics_manager

app = FastAPI(
    title="Health Data Exchange API",
    description="API for secure health data exchange and analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    permissions: List[Permission]

@app.post("/register")
def register_org(
    name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    type: str = Form(...),
    location: str = Form(...),
    password: str = Form(...),
    privacy_accepted: bool = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(Organization).filter_by(email=email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        org_type = OrgType[type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid organization type")

    # Map organization type to user role
    role_mapping = {
        "HOSPITAL": UserRole.DOCTOR,
        "LABORATORY": UserRole.LAB_TECHNICIAN,
        "PHARMACY": UserRole.PHARMACIST,
        "CLINIC": UserRole.DOCTOR,
    }
    user_role = role_mapping.get(type.upper(), UserRole.PATIENT)

    hashed_pw = hash_password(password)
    org = Organization(
        name=name,
        email=email,
        contact=contact,
        type=org_type,
        location=location,
        privacy_accepted=privacy_accepted,
        password_hash=hashed_pw,
        role=user_role
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return {"message": "Organization registered successfully"}

@app.post("/login", response_model=TokenResponse)
def login_org(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    org = db.query(Organization).filter_by(email=email).first()
    if not org or not verify_password(password, org.password_hash):
        raise HTTPException(
            status_code=401, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens with role, permissions, and organization ID
    access_token = create_access_token({
        "sub": org.email,
        "id": org.id,  # Include organization ID
        "role": org.role,
        "permissions": [p.value for p in get_user_permissions(org.role)]
    })
    
    refresh_token = create_refresh_token({
        "sub": org.email,
        "id": org.id,  # Include organization ID
        "role": org.role
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes
    }

@app.post("/refresh-token", response_model=TokenResponse)
def refresh_token(refresh_token: str = Form(...), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        
        org = db.query(Organization).filter_by(email=payload["sub"]).first()
        if not org:
            raise HTTPException(
                status_code=401,
                detail="Organization not found"
            )
        
        # Create new tokens with organization ID
        access_token = create_access_token({
            "sub": org.email,
            "id": org.id,  # Include organization ID
            "role": org.role,
            "permissions": [p.value for p in get_user_permissions(org.role)]
        })
        
        new_refresh_token = create_refresh_token({
            "sub": org.email,
            "id": org.id,  # Include organization ID
            "role": org.role
        })
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

@app.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter_by(email=current_user["sub"]).first()
    if not org:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": org.id,
        "email": org.email,
        "name": org.name,
        "role": org.role,
        "permissions": current_user["permissions"]
    }

@app.post("/upload", response_model=dict)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(...),
    current_user: dict = Depends(require_permissions([Permission.WRITE_PATIENT_DATA])),
    db: Session = Depends(get_db),
):
    try:
        print(f"Starting upload process for file: {file.filename}, category: {category}")
        print(f"Current user: {current_user}")
        
        # Check for force upload header
        force_upload = request.headers.get('X-Force-Upload', '').lower() == 'true'
        print(f"Force upload: {force_upload}")
        
        # Get the organization by email from the token
        org = db.query(Organization).filter_by(email=current_user["sub"]).first()
        if not org:
            print(f"Organization not found for email: {current_user['sub']}")
            raise HTTPException(status_code=404, detail="Organization not found")

        # Verify organization ID matches the token
        if str(org.id) != str(current_user.get("id")):
            print(f"Organization ID mismatch: {org.id} != {current_user.get('id')}")
            raise HTTPException(
                status_code=403,
                detail="Access denied: Organization ID mismatch"
            )

        print(f"Organization verified: {org.id}")

        # Verify organization is active
        if not org.is_active:
            print(f"Organization {org.id} is not active")
            raise HTTPException(
                status_code=403,
                detail="Account is not active"
            )

        # Skip email verification check if force upload is enabled
        if not force_upload and not org.email_verified:
            print(f"Email not verified for organization {org.id}")
            raise HTTPException(
                status_code=403,
                detail="Please verify your email address before uploading files"
            )

        # Validate file extension
        if not allowed_file_extension(file.filename):
            print(f"Invalid file extension for file: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only CSV files are allowed."
            )
        
        # Validate file size
        try:
            if not validate_file_size(file):
                print(f"File size too large: {file.filename}")
                raise HTTPException(
                    status_code=400,
                    detail="File size too large. Maximum size is 10MB."
                )
        except Exception as e:
            error_msg = f"Error checking file size: {str(e)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        try:
            # Create organization-specific upload directory
            org_upload_dir = os.path.join(UPLOAD_DIR, str(org.id))
            os.makedirs(org_upload_dir, exist_ok=True)
            print(f"Organization upload directory: {org_upload_dir}")

            # Create a unique filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{category}_{timestamp}_{file.filename}"
            safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in "._-")
            file_path = os.path.join(org_upload_dir, safe_filename)
            print(f"Target file path: {file_path}")
            
            # Get file size and mime type
            file.file.seek(0, os.SEEK_END)
            file_size = file.file.tell()
            file.file.seek(0)
            
            mime_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
            print(f"File details - Size: {file_size} bytes, MIME type: {mime_type}")
            
            # Create upload entry first with pending status
            upload_entry = Upload(
                filename=safe_filename,
                original_filename=file.filename,
                category=category,
                org_id=org.id,
                file_size=file_size,
                mime_type=mime_type,
                status="pending"
            )
            db.add(upload_entry)
            db.commit()
            db.refresh(upload_entry)
            print(f"Created upload entry in database with ID: {upload_entry.id}")

            # Save the file
            print("Saving file to disk...")
            try:
                # First save the raw binary data
                file_content = file.file.read()
                file.file.seek(0)  # Reset file pointer
                
                with open(file_path, "wb") as buffer:
                    buffer.write(file_content)
                print(f"File saved successfully to {file_path}")
                
                # Verify file was saved
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File was not saved: {file_path}")
                
                saved_size = os.path.getsize(file_path)
                if saved_size != file_size:
                    raise ValueError(f"Saved file size ({saved_size}) does not match uploaded size ({file_size})")
                
                # Try to detect the encoding
                encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
                detected_encoding = None
                file_text = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            file_text = f.read()
                            if file_text and ',' in file_text:  # Basic CSV check
                                detected_encoding = encoding
                                print(f"Successfully read file with encoding: {encoding}")
                                break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error reading with encoding {encoding}: {str(e)}")
                        continue
                
                if not detected_encoding:
                    raise ValueError("Could not detect valid CSV encoding")
                
                # Rewrite the file with the correct encoding if needed
                if detected_encoding != 'utf-8':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_text)
                    print(f"Converted file from {detected_encoding} to UTF-8")
                
            except Exception as e:
                print(f"Error saving file: {str(e)}")
                upload_entry.status = "error"
                upload_entry.error_message = f"Failed to save file: {str(e)}"
                db.commit()
                raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

            # Update status to processing
            upload_entry.status = "processing"
            db.commit()

            try:
                print(f"Running analysis on file: {file_path}")
                analysis_result = run_analysis(file_path, category)
                print(f"Analysis result: {json.dumps(analysis_result, indent=2)}")
                
                if not analysis_result:
                    error_msg = "Analysis failed: No results returned"
                    print(error_msg)
                    upload_entry.status = "error"
                    upload_entry.error_message = error_msg
                    db.commit()
                    return {
                        "message": error_msg,
                        "result_id": upload_entry.id,
                        "result": upload_entry.to_dict()
                    }
                
                if "error" in analysis_result:
                    print(f"Analysis error: {analysis_result['error']}")
                    upload_entry.status = "error"
                    upload_entry.error_message = analysis_result["error"]
                else:
                    print("Analysis completed successfully")
                    upload_entry.status = "completed"
                    upload_entry.result = analysis_result
                    upload_entry.processed_at = datetime.utcnow()
                
                db.commit()
                print(f"Database updated. Upload entry ID: {upload_entry.id}")
                
                return_data = upload_entry.to_dict()
                print(f"Returning data: {json.dumps(return_data, indent=2)}")
                
                return {
                    "message": "File uploaded and processed successfully",
                    "result_id": upload_entry.id,
                    "result": return_data
                }

            except Exception as e:
                error_msg = f"Error during analysis: {str(e)}"
                print(error_msg)
                upload_entry.status = "error"
                upload_entry.error_message = error_msg
                db.commit()
                raise HTTPException(status_code=500, detail=error_msg)

        except Exception as e:
            error_msg = f"Error during file upload: {str(e)}"
            print(error_msg)
            # Clean up file if something goes wrong
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Cleaned up file: {file_path}")
                except Exception as cleanup_error:
                    print(f"Failed to clean up file: {str(cleanup_error)}")
            raise HTTPException(status_code=500, detail=error_msg)

    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/result/{result_id}")
def get_result(
    result_id: int,
    current_user: dict = Depends(require_permissions([Permission.READ_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    try:
        print(f"Fetching result {result_id} for user {current_user['sub']}")
        
        # Get the organization by email from the token
        org = db.query(Organization).filter_by(email=current_user["sub"]).first()
        if not org:
            print(f"Organization not found for email: {current_user['sub']}")
            raise HTTPException(status_code=404, detail="Organization not found")

        print(f"Found organization: {org.id}")

        # Find the upload with proper org_id
        upload = db.query(Upload).filter(
            Upload.id == result_id,
            Upload.org_id == org.id
        ).first()

        if not upload:
            print(f"Result {result_id} not found for organization {org.id}")
            raise HTTPException(status_code=404, detail="Result not found")

        print(f"Found result. Status: {upload.status}")
        return_data = upload.to_dict()
        print(f"Returning data: {json.dumps(return_data, indent=2)}")
        return return_data

    except Exception as e:
        print(f"Error in get_result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uploads", response_model=List[dict])
def list_uploads(
    skip: int = 0, 
    limit: int = 10,
    current_user: dict = Depends(require_permissions([Permission.READ_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    try:
        print(f"Listing uploads for user {current_user['sub']}")
        
        # Get the organization by email from the token
        org = db.query(Organization).filter_by(email=current_user["sub"]).first()
        if not org:
            print(f"Organization not found for email: {current_user['sub']}")
            raise HTTPException(status_code=404, detail="Organization not found")

        print(f"Found organization: {org.id}")

        # Get uploads for the organization
        uploads = db.query(Upload).filter_by(org_id=org.id)\
            .order_by(Upload.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        print(f"Found {len(uploads)} uploads")
        
        # Convert to dict format
        upload_list = [u.to_dict() for u in uploads]
        print(f"Returning upload list with {len(upload_list)} items")
        
        return upload_list

    except Exception as e:
        print(f"Error in list_uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/uploads/{upload_id}")
def delete_upload(
    upload_id: int,
    current_user: dict = Depends(require_permissions([Permission.WRITE_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    # Get the organization by email from the token
    org = db.query(Organization).filter_by(email=current_user["sub"]).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Find the upload
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.org_id == org.id
    ).first()

    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    try:
        # Delete the physical file if it exists
        file_path = os.path.join(UPLOAD_DIR, upload.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the database record
        db.delete(upload)
        db.commit()

        return {"message": "Upload deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uploads/{upload_id}")
def get_upload(
    upload_id: int,
    current_user: dict = Depends(require_permissions([Permission.READ_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    try:
        print(f"Fetching upload {upload_id} for user {current_user['sub']}")
        
        # Get the organization by email from the token
        org = db.query(Organization).filter_by(email=current_user["sub"]).first()
        if not org:
            print(f"Organization not found for email: {current_user['sub']}")
            raise HTTPException(status_code=404, detail="Organization not found")

        print(f"Found organization: {org.id}")

        # Find the upload
        upload = db.query(Upload).filter(
            Upload.id == upload_id,
            Upload.org_id == org.id
        ).first()

        if not upload:
            print(f"Upload {upload_id} not found for organization {org.id}")
            raise HTTPException(status_code=404, detail="Upload not found")

        print(f"Found upload. Status: {upload.status}")
        
        # Convert to dict and check result
        return_data = upload.to_dict()
        print(f"Upload data: {json.dumps(return_data, indent=2)}")
        
        if not return_data.get('result'):
            print("Warning: Upload has no result data")
            return_data['result'] = {
                "status": "error",
                "message": "No analysis results available"
            }
        
        return return_data
        
    except Exception as e:
        print(f"Error in get_upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

@app.post("/send-otp")
async def send_otp(request: OTPRequest):
    try:
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', request.email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        # Check for disposable email domains
        disposable_domains = [
            'tempmail.com', 'throwawaymail.com', 'mailinator.com', 'guerrillamail.com',
            'sharklasers.com', 'yopmail.com', 'temp-mail.org', 'fakeinbox.com',
            'temp-mail.io', 'tempmail.net', 'tempail.com', 'tempmail.org',
            'temp-mail.ru', 'tempmailaddress.com', 'tempmailbox.com', 'tempmail.co',
            'tempmail.de', 'tempmail.fr', 'tempmail.it', 'tempmail.nl',
            'tempmail.pl', 'tempmail.pt', 'tempmail.ru', 'tempmail.se',
            'tempmail.sk', 'tempmail.es', 'tempmail.uk', 'tempmail.us'
        ]
        
        domain = request.email.split('@')[1].lower()
        if domain in disposable_domains:
            raise HTTPException(status_code=400, detail="Disposable email addresses are not allowed")

        otp = generate_otp(request.email)
        if send_otp_email(request.email, otp):
            return {"message": "OTP sent successfully"}
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-otp")
async def verify_otp_endpoint(verify_data: OTPVerify):
    try:
        if verify_otp(verify_data.email, verify_data.otp):
            return {"message": "OTP verified successfully"}
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class EmailVerify(BaseModel):
    email: EmailStr

@app.post("/verify-email")
async def verify_email(request: EmailVerify):
    try:
        # Basic email format validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', request.email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        # Extract domain from email
        domain = request.email.split('@')[1]

        try:
            # Check if domain has MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                raise HTTPException(status_code=400, detail="Invalid email domain")

            # Additional checks for common email providers
            if domain.lower() in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                # For common providers, we can do additional validation
                username = request.email.split('@')[0]
                if len(username) < 3 or len(username) > 30:
                    raise HTTPException(status_code=400, detail="Invalid email username length")
                
                # Check for common patterns in fake emails
                if re.match(r'^(test|demo|fake|dummy|temp)', username.lower()):
                    raise HTTPException(status_code=400, detail="Please use a real email address")

            return {"isValid": True, "message": "Email is valid"}

        except dns.resolver.NXDOMAIN:
            raise HTTPException(status_code=400, detail="Invalid email domain")
        except dns.resolver.NoAnswer:
            raise HTTPException(status_code=400, detail="Invalid email domain")
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid email address")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reset-password")
async def reset_password(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        email = data.get("email")
        new_password = data.get("password")

        if not email or not new_password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        # Validate password requirements
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        if not re.search(r'[A-Za-z]', new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one letter")
        if not re.search(r'\d', new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one number")

        # Find the user in the database
        user = db.query(Organization).filter(Organization.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Hash the new password
        hashed_password = hash_password(new_password)

        # Update the user's password
        user.password_hash = hashed_password
        db.commit()

        return {"message": "Password reset successful"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations", response_model=List[UserResponse])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow admin users
    if str(current_user["role"]).lower() != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return [
        {
            "id": org.id,
            "email": org.email,
            "name": org.name,
            "role": org.role,
            "permissions": [p.value for p in get_user_permissions(org.role)]
        }
        for org in organizations
    ]

class ProfileUpdate(BaseModel):
    name: str
    email: str
    contact: str
    type: str
    location: str

@app.put("/update-profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get the organization by email from the token
        org = db.query(Organization).filter(Organization.email == current_user["sub"]).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Validate organization type
        try:
            org_type = OrgType[profile_data.type.upper()]
        except KeyError:
            valid_types = ", ".join([t.name for t in OrgType])
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid organization type. Valid types are: {valid_types}"
            )

        # Update organization details
        org.name = profile_data.name
        org.email = profile_data.email
        org.contact = profile_data.contact
        org.type = org_type
        org.location = profile_data.location

        try:
            db.commit()
            db.refresh(org)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Failed to update profile. The email address may already be in use."
            )

        # Return updated user data
        return {
            "id": org.id,
            "name": org.name,
            "email": org.email,
            "contact": org.contact,
            "type": org.type.value,
            "location": org.location,
            "role": org.role.value,
            "token": current_user.get("token")  # Include the token in the response
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@app.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get the organization by email from the token
        org = db.query(Organization).filter(Organization.email == current_user["sub"]).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Verify current password
        if not verify_password(password_data.current_password, org.password_hash):
            print(f"Password verification failed for user {current_user['sub']}")
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # Validate new password requirements
        validation_errors = []
        if len(password_data.new_password) < 6:
            validation_errors.append("Password must be at least 6 characters long")
        if not re.search(r'[A-Za-z]', password_data.new_password):
            validation_errors.append("Password must contain at least one letter")
        if not re.search(r'\d', password_data.new_password):
            validation_errors.append("Password must contain at least one number")
        
        if validation_errors:
            print(f"Password validation failed for user {current_user['sub']}: {validation_errors}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Password validation failed",
                    "errors": validation_errors
                }
            )

        # Hash and update the new password
        org.password_hash = hash_password(password_data.new_password)
        db.commit()
        print(f"Password successfully changed for user {current_user['sub']}")

        return {"message": "Password changed successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error during password change for user {current_user['sub']}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class HealthDataInput(BaseModel):
    patient_id: str
    data_type: str
    data: dict
    timestamp: str

class ComputationInput(BaseModel):
    computation_type: str
    data_points: List[dict]

@app.post("/secure-health-data")
async def upload_health_data(
    data: HealthDataInput,
    current_user: dict = Depends(require_permissions([Permission.WRITE_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    try:
        # Log incoming data for debugging
        print(f"Received data: {data}")
        print(f"Current user: {current_user}")
        
        # Create new health record
        record = SecureHealthRecord(
            patient_id=data.patient_id,
            org_id=current_user["id"],
            data_type=data.data_type
        )
        
        try:
            # Set and encrypt the data
            record.set_data({
                "patient_id": data.patient_id,
                "data_type": data.data_type,
                "data": data.data,
                "timestamp": data.timestamp
            })
        except Exception as e:
            print(f"Error in set_data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to encrypt data: {str(e)}")
        
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as e:
            print(f"Database error: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return {"message": "Health data uploaded successfully", "record_id": record.id}
    except Exception as e:
        print(f"Unexpected error in upload_health_data: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/secure-health-data/{record_id}")
async def get_health_data(
    record_id: int,
    current_user: dict = Depends(require_permissions([Permission.READ_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    record = db.query(SecureHealthRecord).filter(
        SecureHealthRecord.id == record_id,
        SecureHealthRecord.org_id == current_user["id"]
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return record.get_data()

@app.post("/computations")
def create_computation(org_id: int, computation_type: str, db: Session = Depends(get_db)):
    """Create a new secure computation session"""
    service = SecureComputationService(db)
    computation_id = service.create_computation(org_id, computation_type)
    return {"computation_id": computation_id}

@app.post("/computations/{computation_id}/join")
def join_computation(computation_id: str, org_id: int, db: Session = Depends(get_db)):
    """Join an existing secure computation session"""
    service = SecureComputationService(db)
    success = service.join_computation(computation_id, org_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not join computation")
    return {"status": "success"}

@app.post("/computations/{computation_id}/submit")
def submit_data(computation_id: str, org_id: int, data: List[float], db: Session = Depends(get_db)):
    """Submit data for secure computation"""
    service = SecureComputationService(db)
    success = service.submit_data(computation_id, org_id, data)
    if not success:
        raise HTTPException(status_code=400, detail="Could not submit data")
    return {"status": "success"}

@app.get("/computations/{computation_id}")
def get_computation_result(computation_id: str, db: Session = Depends(get_db)):
    """Get the result of a secure computation"""
    service = SecureComputationService(db)
    result = service.get_computation_result(computation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Computation not found or not completed")
    return result

@app.post("/computations/{computation_id}/compute")
def perform_computation(computation_id: str, db: Session = Depends(get_db)):
    """Perform the secure computation"""
    service = SecureComputationService(db)
    success = service.perform_computation(computation_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not perform computation")
    return {"status": "success"}

@app.get("/computations")
def list_computations(org_id: int, db: Session = Depends(get_db)):
    """List all computations for an organization"""
    service = SecureComputationService(db)
    return service.list_computations(org_id)

@app.get("/analytics")
async def get_analytics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics data for the dashboard."""
    try:
        # Get total uploads
        total_uploads = db.query(Upload).count()
        
        # Get active users in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.query(Organization).filter(
            Organization.last_login >= thirty_days_ago
        ).count()
        
        # Get total analysis count
        total_analysis = db.query(Upload).filter(
            Upload.status == "completed"
        ).count()
        
        # Get recent activity
        recent_uploads = db.query(Upload).filter(
            Upload.org_id == current_user.get("id")
        ).order_by(
            Upload.created_at.desc()
        ).limit(10).all()
        
        recent_activity = []
        for upload in recent_uploads:
            recent_activity.append({
                "type": "upload" if upload.status == "pending" else "analysis",
                "description": f"{upload.filename} - {upload.category}",
                "timestamp": upload.created_at.strftime("%Y-%m-%d %H:%M")
            })
        
        # Get aggregated health metrics
        health_metrics = aggregate_health_metrics(current_user.get("id"), db)
        
        return {
            "total_uploads": total_uploads,
            "active_users": active_users,
            "total_analysis": total_analysis,
            "recent_activity": recent_activity,
            "health_metrics": health_metrics
        }
    except Exception as e:
        print(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch analytics data"
        )

def aggregate_health_metrics(user_id: int, db: Session):
    """Aggregate health metrics for a user."""
    try:
        print(f"Aggregating health metrics for user {user_id}")
        # Get user's completed uploads
        uploads = db.query(Upload).filter(
            Upload.org_id == user_id,
            Upload.status == "completed"
        ).all()
        print(f"Found {len(uploads)} completed uploads")
        
        # Aggregate metrics from all uploads
        aggregated_data = {
            "blood_sugar": [],
            "blood_pressure": [],
            "heart_rate": []
        }
        
        for upload in uploads:
            print(f"Processing upload {upload.id}")
            try:
                if not upload.result:
                    print(f"Upload {upload.id} has no result")
                    continue
                    
                if isinstance(upload.result, str):
                    result = json.loads(upload.result)
                else:
                    result = upload.result
                
                if not isinstance(result, dict) or "analysis" not in result:
                    print(f"Upload {upload.id} has invalid result format")
                    continue
                    
                analysis = result["analysis"]
                
                # Add metrics to respective arrays
                for metric in ["blood_sugar", "blood_pressure", "heart_rate"]:
                    if metric in analysis and "raw_values" in analysis[metric]:
                        values = analysis[metric]["raw_values"]
                        if isinstance(values, list):
                            aggregated_data[metric].extend(values)
                            print(f"Added {len(values)} values for {metric}")
                
            except Exception as e:
                print(f"Error processing upload {upload.id}: {str(e)}")
                continue
        
        # Calculate statistics for each metric
        metrics_summary = {}
        for metric, values in aggregated_data.items():
            if values:
                try:
                    metrics_summary[metric] = {
                        "average": float(sum(values)) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values),
                        "latest": values[-1] if values else None,
                        "trend": "up" if len(values) > 1 and values[-1] > values[-2] else "down",
                        "raw_values": values[-10:]  # Send last 10 values for trending
                    }
                    print(f"Calculated statistics for {metric}: {metrics_summary[metric]}")
                except Exception as e:
                    print(f"Error calculating statistics for {metric}: {str(e)}")
                    continue
        
        if not metrics_summary:
            print("No metrics could be calculated")
            return {
                "blood_sugar": {"count": 0, "raw_values": []},
                "blood_pressure": {"count": 0, "raw_values": []},
                "heart_rate": {"count": 0, "raw_values": []}
            }
            
        return metrics_summary
    except Exception as e:
        print(f"Error in aggregate_health_metrics: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "blood_sugar": {"count": 0, "raw_values": []},
            "blood_pressure": {"count": 0, "raw_values": []},
            "heart_rate": {"count": 0, "raw_values": []}
        }

# Initialize secure computation service
secure_health_computation = SecureHealthMetricsComputation()

class SecureComputationRequest(BaseModel):
    metric_type: str
    participating_orgs: List[str]

class MetricSubmission(BaseModel):
    value: float

@app.post("/secure-computations/initialize")
async def initialize_secure_computation(
    request: SecureComputationRequest,
    current_user: dict = Depends(require_permissions([Permission.WRITE_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    """Initialize a new secure multiparty computation"""
    try:
        computation_id = str(uuid.uuid4())
        result = secure_health_computation.initialize_computation(
            computation_id,
            request.metric_type,
            request.participating_orgs
        )
        return {
            "computation_id": computation_id,
            "status": "initialized",
            "participating_orgs": request.participating_orgs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/secure-computations/{computation_id}/submit")
async def submit_metric(
    computation_id: str,
    submission: MetricSubmission,
    current_user: dict = Depends(require_permissions([Permission.WRITE_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    """Submit a metric value for secure computation"""
    try:
        org_id = str(current_user["id"])
        result = secure_health_computation.submit_metric(
            computation_id,
            org_id,
            submission.value
        )
        return {
            "status": "success",
            "message": "Metric submitted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/secure-computations/{computation_id}/compute")
async def compute_aggregate_metrics(
    computation_id: str,
    current_user: dict = Depends(require_permissions([Permission.WRITE_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    """Compute aggregate metrics using secure multiparty computation"""
    try:
        result = secure_health_computation.compute_aggregate_metrics(computation_id)
        if result:
            return {
                "status": "success",
                "result": result
            }
        raise HTTPException(status_code=400, detail="Computation failed or not ready")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/secure-computations/{computation_id}/status")
async def get_computation_status(
    computation_id: str,
    current_user: dict = Depends(require_permissions([Permission.READ_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    """Get the status of a secure computation"""
    try:
        status = secure_health_computation.get_computation_status(computation_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/secure-computations")
async def list_computations(
    current_user: dict = Depends(require_permissions([Permission.READ_PATIENT_DATA])),
    db: Session = Depends(get_db)
):
    """List all secure computations for the organization"""
    try:
        org_id = str(current_user["id"])
        computations = []
        for comp_id, comp in secure_health_computation.computations.items():
            if org_id in comp['organizations']:
                computations.append({
                    "computation_id": comp_id,
                    "status": comp['status'],
                    "metric_type": comp['metric_type'],
                    "start_time": comp['start_time'],
                    "end_time": comp.get('end_time'),
                    "participating_orgs": list(comp['organizations']),
                    "submitted_orgs": list(comp['shares_submitted'])
                })
        return computations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    try:
        # Get the token from the query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return

        # Validate the token
        try:
            payload = decode_access_token(token)
            org_id = payload.get("id")
            if not org_id:
                await websocket.close(code=4002, reason="Invalid token")
                return
        except Exception as e:
            await websocket.close(code=4003, reason="Invalid token")
            return

        # Connect the WebSocket
        await metrics_manager.connect(websocket, org_id)
        
        try:
            while True:
                # Keep the connection alive and handle incoming messages if needed
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            metrics_manager.disconnect(websocket, org_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=4000)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(secure_computations.router, prefix="/secure-computations", tags=["Secure Computations"])
app.include_router(analytics.router, tags=["Analytics"])

@app.get("/")
async def root():
    return {
        "message": "Health Data Exchange API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
