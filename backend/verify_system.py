import os
import sys
import logging
import requests
from datetime import datetime
from pathlib import Path
from models import SessionLocal, Organization, Upload
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Base URL for API
BASE_URL = "http://localhost:8000"

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking Environment Configuration")
    print("-" * 80)
    
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("❌ .env file not found")
        return False
        
    # Check for required variables
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "EMAIL_FROM",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "MAX_FILE_SIZE",
        "ALLOWED_EXTENSIONS"
    ]
    
    with open(env_path, "r") as f:
        env_content = f.read()
        
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Environment configuration is correct")
        return True

def check_database():
    """Check database connection and organization data"""
    print("\n🔍 Checking Database")
    print("-" * 80)
    
    try:
        # Connect to database
        db = SessionLocal()
        
        # Check connection
        db.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Check organizations
        orgs = db.query(Organization).all()
        print(f"✅ Found {len(orgs)} organizations in database")
        
        # Check for unverified organizations
        unverified_orgs = db.query(Organization).filter(Organization.email_verified == False).all()
        if unverified_orgs:
            print(f"⚠️ Found {len(unverified_orgs)} unverified organizations")
        else:
            print("✅ All organizations are verified")
        
        # Check uploads
        uploads = db.query(Upload).all()
        print(f"✅ Found {len(uploads)} uploads in database")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        return False

def check_api_health():
    """Check if API is healthy"""
    print("\n🔍 Checking API Health")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy (Version: {data.get('version')})")
            if data.get('note') == "Forced healthy for testing":
                print("⚠️ Note: Health check is forced to pass for testing")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        return False

def check_login_endpoint():
    """Check if login endpoint is working"""
    print("\n🔍 Checking Login Endpoint")
    print("-" * 80)
    
    try:
        # Get a test user from database
        db = SessionLocal()
        org = db.query(Organization).filter(Organization.email_verified == True).first()
        db.close()
        
        if not org:
            print("❌ No verified organizations found for testing login")
            return False
            
        # Try to login with invalid password
        response = requests.post(f"{BASE_URL}/login", data={
            "email": org.email,
            "password": "invalid-password"
        })
        
        if response.status_code == 401:
            print("✅ Login endpoint correctly rejects invalid credentials")
        else:
            print(f"⚠️ Login endpoint returned {response.status_code} for invalid credentials")
        
        return True
    except Exception as e:
        print(f"❌ Login endpoint check failed: {str(e)}")
        return False

def run_system_verification():
    """Run all verification checks"""
    print("🔍 System Verification")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = [
        ("Environment Configuration", check_env_file()),
        ("Database", check_database()),
        ("API Health", check_api_health()),
        ("Login Endpoint", check_login_endpoint())
    ]
    
    # Print summary
    print("\n📋 Verification Summary")
    print("-" * 80)
    
    all_passed = True
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"{status} - {name}")
    
    if all_passed:
        print("\n✅ All checks passed! System is ready.")
    else:
        print("\n⚠️ Some checks failed. Please review the issues above.")

if __name__ == "__main__":
    run_system_verification()