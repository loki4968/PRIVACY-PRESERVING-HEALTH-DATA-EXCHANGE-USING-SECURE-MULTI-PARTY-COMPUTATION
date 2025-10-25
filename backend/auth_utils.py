import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import jwt
from enum import Enum
from config import Settings

# Get settings from config
settings = Settings()

# Secret key for JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

print(f"Using SECRET_KEY: {SECRET_KEY[:5]}...")
print(f"Using ALGORITHM: {ALGORITHM}")
print(f"Using ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
print(f"Using REFRESH_TOKEN_EXPIRE_DAYS: {REFRESH_TOKEN_EXPIRE_DAYS}")

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
    SECURE_COMPUTATIONS = "secure_computations"

# Role-based permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: [p for p in Permission],
    UserRole.DOCTOR: [
        Permission.READ_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,
        Permission.READ_LAB_RESULTS,
        Permission.PRESCRIBE_MEDICATION,
        Permission.VIEW_ANALYTICS,
        Permission.SECURE_COMPUTATIONS
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
    
    # Add permissions to token if role is present but permissions are not
    if "role" in data and "permissions" not in data:
        try:
            user_role = UserRole(data["role"])
            to_encode["permissions"] = get_user_permissions(user_role)
        except ValueError:
            # If role is not a valid UserRole enum value
            pass
    
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
        print(f"Decoding token: {token[:20]}...")
        # First try to decode without verification to inspect the token
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            print(f"Unverified payload: {unverified_payload}")
        except Exception as e:
            print(f"Error decoding unverified token: {e}")
            
        # Now decode with verification
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Verified payload: {payload}")
        
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            print("Token expired")
            return None
            
        if payload.get("type") != "access" and "type" in payload:
            print(f"Invalid token type: {payload.get('type')}")
            return None
            
        # If role is in the payload but permissions are not, add them
        if "role" in payload and "permissions" not in payload:
            role = payload["role"]
            try:
                user_role = UserRole(role)
                payload["permissions"] = get_user_permissions(user_role)
                print(f"Added permissions for role {role}: {payload['permissions']}")
            except ValueError as e:
                print(f"Invalid role value: {role}, error: {e}")
                # If role is not a valid UserRole enum value
                pass
                
        return payload
    except jwt.PyJWTError as e:
        print(f"JWT decode error: {e}")
        return None

def check_permission(user_role: UserRole, required_permission: Permission) -> bool:
    """Check if a user role has the required permission."""
    if user_role not in ROLE_PERMISSIONS:
        return False
    return required_permission in ROLE_PERMISSIONS[user_role]

def get_user_permissions(user_role: UserRole) -> List[Permission]:
    """Get all permissions for a given user role."""
    return ROLE_PERMISSIONS.get(user_role, [])
