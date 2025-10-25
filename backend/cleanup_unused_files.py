import os
import sys
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Backup directory
BACKUP_DIR = PROJECT_ROOT / "backup_files"

# Files that are known to be safe to remove
SAFE_TO_REMOVE = [
    # Test files that are no longer needed
    "backend/test_unverified_login.py",
    "backend/test_new_registration.py",
    "backend/fix_registration.py",
    # Temporary files
    "**/*.pyc",
    "**/__pycache__",
    "**/.pytest_cache",
    # Log files
    "**/*.log",
    # Temporary database files
    "**/*.db-journal",
]

# Critical files that should never be removed
CRITICAL_FILES = [
    # Core application files
    "backend/main.py",
    "backend/models.py",
    "backend/database.py",
    "backend/config.py",
    "backend/auth_utils.py",
    "backend/otp_utils.py",
    # Configuration files
    "backend/.env",
    ".env",
    # Frontend core files
    "app/page.jsx",
    "app/layout.jsx",
    "app/components/LoginForm.jsx",
    "app/components/RegisterForm.jsx",
    # Package management files
    "package.json",
    "requirements.txt",
    # Documentation
    "README.md",
    "DEPLOYMENT.md",
    "EMAIL_CONFIGURATION.md",
]

def backup_file(file_path):
    """Create a backup of the file before removing it"""
    try:
        # Create backup directory if it doesn't exist
        if not BACKUP_DIR.exists():
            BACKUP_DIR.mkdir(parents=True)
            
        # Get relative path to maintain directory structure in backup
        rel_path = Path(file_path).relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / rel_path
        
        # Create parent directories if they don't exist
        if not backup_path.parent.exists():
            backup_path.parent.mkdir(parents=True)
            
        # Copy file to backup location
        shutil.copy2(file_path, backup_path)
        logging.info(f"Backed up {file_path} to {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to backup {file_path}: {e}")
        return False

def is_critical_file(file_path):
    """Check if the file is in the critical files list"""
    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
    rel_path = rel_path.replace("\\", "/")  # Normalize path separators
    
    for critical_file in CRITICAL_FILES:
        if rel_path == critical_file:
            return True
    return False

def is_safe_to_remove(file_path):
    """Check if the file is safe to remove"""
    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
    rel_path = rel_path.replace("\\", "/")  # Normalize path separators
    
    for pattern in SAFE_TO_REMOVE:
        # Handle glob patterns
        if "*" in pattern:
            import fnmatch
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        # Direct match
        elif rel_path == pattern:
            return True
    return False

def cleanup_unused_files(dry_run=True):
    """Identify and remove unused files"""
    removed_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"{'🔍 DRY RUN: ' if dry_run else ''}Cleaning up unused files...")
    print("=" * 80)
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip the backup directory
        if os.path.abspath(root).startswith(os.path.abspath(BACKUP_DIR)):
            continue
            
        # Skip version control directories
        if ".git" in dirs:
            dirs.remove(".git")
        if "node_modules" in dirs:
            dirs.remove("node_modules")
            
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip critical files
            if is_critical_file(file_path):
                logging.info(f"Skipping critical file: {file_path}")
                skipped_count += 1
                continue
                
            # Check if file is safe to remove
            if is_safe_to_remove(file_path):
                try:
                    if not dry_run:
                        # Backup file before removing
                        if backup_file(file_path):
                            # Remove file
                            os.remove(file_path)
                            logging.info(f"Removed: {file_path}")
                            removed_count += 1
                        else:
                            logging.warning(f"Skipped removal due to backup failure: {file_path}")
                            error_count += 1
                    else:
                        logging.info(f"Would remove: {file_path}")
                        removed_count += 1
                except Exception as e:
                    logging.error(f"Error removing {file_path}: {e}")
                    error_count += 1
    
    # Print summary
    print("\nCleanup Summary:")
    print("-" * 80)
    print(f"{'Would remove' if dry_run else 'Removed'}: {removed_count} files")
    print(f"Skipped: {skipped_count} files")
    print(f"Errors: {error_count}")
    
    if dry_run:
        print("\n⚠️ This was a dry run. No files were actually removed.")
        print("Run with --force to actually remove the files.")
    else:
        print(f"\n✅ Cleanup complete! Removed {removed_count} files.")
        print(f"✅ Backups saved to {BACKUP_DIR}")

if __name__ == "__main__":
    # Check if --force flag is provided
    force = "--force" in sys.argv
    
    # Run cleanup
    cleanup_unused_files(dry_run=not force)