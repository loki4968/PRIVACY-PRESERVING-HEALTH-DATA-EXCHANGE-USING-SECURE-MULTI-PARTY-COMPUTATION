from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.models import Organization
from backend.dependencies import get_db
from backend.auth_utils import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_access_token, UserRole, Permission, get_user_permissions
)
from pydantic import BaseModel, EmailStr

router = APIRouter()

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

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=TokenResponse)
def login(email: str, password: str, db: Session = Depends(get_db)):
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
        "id": org.id,
        "role": org.role,
        "permissions": [p.value for p in get_user_permissions(org.role)]
    })
    
    refresh_token = create_refresh_token({
        "sub": org.email,
        "id": org.id,
        "role": org.role
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes
    }

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(request.refresh_token)
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
            "id": org.id,
            "role": org.role,
            "permissions": [p.value for p in get_user_permissions(org.role)]
        })
        
        new_refresh_token = create_refresh_token({
            "sub": org.email,
            "id": org.id,
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