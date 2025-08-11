import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# File upload settings
UPLOAD_DIR = str(BASE_DIR / "uploads")
ALLOWED_EXTENSIONS = {".csv"}  # Only allow CSV files for now
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

# Database settings
DATABASE_URL = f"sqlite:///{str(BASE_DIR / 'health.db')}"
DATABASE_CONNECT_ARGS = {"check_same_thread": False}

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change in production
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

# API settings
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Health Data Exchange"
VERSION = "1.0.0"
DESCRIPTION = """
Health Data Exchange API allows secure sharing and analysis of health-related data.
"""

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "http://localhost:8000",  # FastAPI backend
]

# Categories for data upload
VALID_CATEGORIES = [
    "blood_test",
    "vital_signs",
    "medical_history",
    "prescription",
    "lab_results",
    "imaging",
    "cardiology",
    "neurology",
    "pediatrics",
    "orthopedics",
    "oncology",
    "endocrinology",
    "immunology",
    "gastroenterology",
    "pulmonology",
    "other"
]
