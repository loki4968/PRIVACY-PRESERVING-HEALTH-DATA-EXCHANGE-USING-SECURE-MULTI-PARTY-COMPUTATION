from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Organization, Upload
from config import DATABASE_URL, DATABASE_CONNECT_ARGS
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args=DATABASE_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def cleanup_organizations():
    """Remove older test organizations and fix registration issues"""
    try:
        # Get all organizations
        orgs = db.query(Organization).all()
        logger.info(f"Found {len(orgs)} organizations in the database")
        
        # Count organizations to be removed
        test_orgs = [org for org in orgs if (
            # Test email patterns
            'test' in org.email.lower() or 
            # Unverified emails older than 7 days
            (not org.email_verified and org.created_at < datetime.utcnow() - timedelta(days=7))
        )]
        
        logger.info(f"Found {len(test_orgs)} test/old organizations to clean up")
        
        # Keep track of which organizations were removed
        removed_orgs = []
        
        # Process each organization
        for org in test_orgs:
            # Skip the main test organization with ID 5 (has uploads)
            if org.id == 5:
                logger.info(f"Skipping organization ID 5 as it has uploads")
                continue
                
            # Check if organization has uploads
            uploads = db.query(Upload).filter(Upload.org_id == org.id).all()
            if uploads:
                logger.info(f"Skipping organization {org.id} ({org.email}) as it has {len(uploads)} uploads")
                continue
            
            # Remove the organization
            logger.info(f"Removing organization {org.id}: {org.email} (created: {org.created_at})")
            db.delete(org)
            removed_orgs.append(org.email)
        
        # Commit changes
        db.commit()
        logger.info(f"Successfully removed {len(removed_orgs)} organizations")
        
        # Fix email verification for remaining organizations
        remaining_orgs = db.query(Organization).filter(Organization.email_verified == False).all()
        logger.info(f"Found {len(remaining_orgs)} organizations with unverified emails")
        
        for org in remaining_orgs:
            logger.info(f"Setting email_verified=True for {org.email}")
            org.email_verified = True
        
        db.commit()
        logger.info("Successfully updated email verification status")
        
        return {
            "removed": removed_orgs,
            "verified": [org.email for org in remaining_orgs]
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up organizations: {str(e)}")
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

def print_organization_summary():
    """Print a summary of organizations after cleanup"""
    try:
        db = SessionLocal()
        orgs = db.query(Organization).all()
        
        print("\nOrganization Summary After Cleanup:")
        print("-" * 80)
        print(f"Total organizations: {len(orgs)}")
        
        verified_count = sum(1 for org in orgs if org.email_verified)
        print(f"Verified organizations: {verified_count}")
        print(f"Unverified organizations: {len(orgs) - verified_count}")
        
        # Print the first 5 organizations
        print("\nSample Organizations:")
        for i, org in enumerate(orgs[:5]):
            print(f"{i+1}. {org.name} ({org.email}) - Verified: {org.email_verified}")
            
    except Exception as e:
        print(f"Error printing summary: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Organization Cleanup Script")
    print("=" * 80)
    
    result = cleanup_organizations()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Removed {len(result['removed'])} organizations")
        print(f"✅ Verified {len(result['verified'])} organizations")
    
    print_organization_summary()