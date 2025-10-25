import sys
import os
sys.path.append('backend')

# Set SQLite database for testing
os.environ['DATABASE_URL'] = 'sqlite:///./test_health_data.db'

from backend.models import Base, engine

def create_test_db():
    print("Creating test database schema...")
    Base.metadata.create_all(bind=engine)
    print("Test database schema created.")

if __name__ == "__main__":
    create_test_db()
