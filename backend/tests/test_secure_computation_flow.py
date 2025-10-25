import unittest
import sys
import os
import json
import uuid
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from database import get_db, SessionLocal
from models import Organization, SecureComputation, OrgType, UserRole

class TestSecureComputationFlow(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()
        
        # Create test organizations
        self.org1 = Organization(
            name="Test Org 1", 
            email="org1@example.com", 
            contact="123-456-7890",
            type=OrgType.HOSPITAL,
            location="Test Location 1",
            privacy_accepted=True,
            password_hash="test_hash",
            role=UserRole.DOCTOR,
            is_active=True, 
            email_verified=True
        )
        self.org2 = Organization(
            name="Test Org 2", 
            email="org2@example.com", 
            contact="123-456-7891",
            type=OrgType.CLINIC,
            location="Test Location 2",
            privacy_accepted=True,
            password_hash="test_hash",
            role=UserRole.DOCTOR,
            is_active=True, 
            email_verified=True
        )
        self.db.add(self.org1)
        self.db.add(self.org2)
        self.db.commit()
        
        # Create tokens for authentication
        self.token1 = "test_token_1"
        self.token2 = "test_token_2"
        
    def tearDown(self):
        # Clean up test data
        self.db.query(SecureComputation).delete()
        self.db.query(Organization).delete()
        self.db.commit()
        self.db.close()
    
    def test_secure_computation_flow(self):
        # Step 1: Create a new computation request
        computation_data = {
            "computation_type": "average",
            "participating_orgs": [str(self.org2.id)],
            "data_type": "blood_sugar",
            "description": "Test computation"
        }
        
        response = self.client.post(
            "/api/secure-computations/",
            json=computation_data,
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        
        self.assertEqual(response.status_code, 201)
        computation_id = response.json()["computation_id"]
        
        # Step 2: Verify the computation was created in the database
        computation = self.db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        self.assertIsNotNone(computation)
        self.assertEqual(computation.status, "pending")
        self.assertEqual(computation.type, "average")
        
        # Step 3: Check for pending requests for the participating organization
        response = self.client.get(
            "/api/secure-computations/pending",
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        
        self.assertEqual(response.status_code, 200)
        pending_computations = response.json()
        self.assertTrue(any(comp["computation_id"] == computation_id for comp in pending_computations))
        
        # Step 4: Accept the computation request
        response = self.client.post(
            f"/api/secure-computations/{computation_id}/accept",
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Step 5: Verify the second user is now a participant
        computation = self.db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        self.assertEqual(computation.status, "accepted")
        
        # Step 6: Submit data for the computation
        data_submission = {
            "value": "120.5",  # Example blood sugar value
            "data_type": "blood_sugar"
        }
        
        response = self.client.post(
            f"/api/secure-computations/{computation_id}/submit-data",
            json=data_submission,
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Step 7: Trigger the computation
        response = self.client.post(
            f"/api/secure-computations/{computation_id}/compute",
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Step 8: Check the computation result
        response = self.client.get(
            f"/api/secure-computations/{computation_id}/result",
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "completed")

if __name__ == "__main__":
    unittest.main()