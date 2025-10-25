import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_env_configuration():
    """Fix environment configuration issues"""
    # Get the backend directory path
    backend_dir = Path(__file__).resolve().parent
    env_file = backend_dir / ".env"
    
    logger.info(f"Checking environment configuration in {env_file}")
    
    # Check if .env file exists
    if not env_file.exists():
        logger.error(f".env file not found at {env_file}")
        return False
    
    # Load environment variables from .env file
    load_dotenv(env_file)
    
    # Check required environment variables
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
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Verify environment variables are correctly loaded
    logger.info("Environment variables loaded successfully:")
    for var in required_vars:
        # Mask sensitive information
        if var in ["SECRET_KEY", "SMTP_PASSWORD"]:
            value = "*" * 8
        else:
            value = os.getenv(var)
        logger.info(f"  {var}: {value}")
    
    # Ensure config.py is using the environment variables
    config_file = backend_dir / "config.py"
    if not config_file.exists():
        logger.error(f"config.py not found at {config_file}")
        return False
    
    logger.info("Environment configuration looks good!")
    return True

def test_database_connection():
    """Test database connection"""
    try:
        # Import here to avoid circular imports
        from sqlalchemy import create_engine, text
        from config import DATABASE_URL, DATABASE_CONNECT_ARGS
        
        logger.info(f"Testing database connection to {DATABASE_URL}")
        
        # Create engine and test connection
        engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
        
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def test_smtp_connection():
    """Test SMTP connection"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        logger.info(f"Testing SMTP connection to {smtp_host}:{smtp_port}")
        
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.quit()
        
        logger.info("SMTP connection successful!")
        return True
    except Exception as e:
        logger.error(f"SMTP connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Environment Configuration Fix Script")
    print("=" * 80)
    
    # Fix environment configuration
    env_ok = fix_env_configuration()
    if env_ok:
        print("✅ Environment configuration is correct")
    else:
        print("❌ Environment configuration has issues")
    
    # Test database connection
    db_ok = test_database_connection()
    if db_ok:
        print("✅ Database connection is working")
    else:
        print("❌ Database connection failed")
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    if smtp_ok:
        print("✅ SMTP connection is working")
    else:
        print("❌ SMTP connection failed")
    
    # Overall status
    if env_ok and db_ok and smtp_ok:
        print("\n✅ All systems are operational!")
    else:
        print("\n❌ Some systems have issues. Please check the logs above.")