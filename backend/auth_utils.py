import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import jwt
from enum import Enum

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    LAB_TECHNICIAN = "lab_technician"
    PHARMACIST = "pharmacist"

class Permission(str, Enum):
    READ_PATIENT_DATA = "read_patient_data"
    WRITE_PATIENT_DATA = "write_patient_data"
    READ_LAB_RESULTS = "read_lab_results"
    WRITE_LAB_RESULTS = "write_lab_results"
    MANAGE_USERS = "manage_users"
    PRESCRIBE_MEDICATION = "prescribe_medication"
    VIEW_ANALYTICS = "view_analytics"

# Role-based permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [p for p in Permission],
    UserRole.DOCTOR: [
        Permission.READ_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,
        Permission.READ_LAB_RESULTS,
        Permission.PRESCRIBE_MEDICATION,
        Permission.VIEW_ANALYTICS
    ],
    UserRole.PATIENT: [
        Permission.READ_PATIENT_DATA,
        Permission.READ_LAB_RESULTS
    ],
    UserRole.LAB_TECHNICIAN: [
        Permission.READ_PATIENT_DATA,
        Permission.WRITE_LAB_RESULTS
    ],
    UserRole.PHARMACIST: [
        Permission.READ_PATIENT_DATA,
        Permission.READ_LAB_RESULTS,
        Permission.PRESCRIBE_MEDICATION
    ]
}

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA-256."""
    salt = os.urandom(32)
    iterations = 100000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    return f"{salt.hex()}${iterations}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using PBKDF2."""
    try:
        salt_hex, iterations, key_hex = hashed_password.split('$')
        salt = bytes.fromhex(salt_hex)
        iterations = int(iterations)
        key = bytes.fromhex(key_hex)
        
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            iterations
        )
        return new_key == key
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with enhanced security."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token with enhanced validation."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            return None
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.PyJWTError:
        return None

def check_permission(user_role: UserRole, required_permission: Permission) -> bool:
    """Check if a user role has the required permission."""
    if user_role not in ROLE_PERMISSIONS:
        return False
    return required_permission in ROLE_PERMISSIONS[user_role]

def get_user_permissions(user_role: UserRole) -> List[Permission]:
    """Get all permissions for a given user role."""
    return ROLE_PERMISSIONS.get(user_role, [])
