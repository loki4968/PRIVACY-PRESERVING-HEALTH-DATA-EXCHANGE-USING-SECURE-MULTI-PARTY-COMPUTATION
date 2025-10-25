import unittest
import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

# Import the modules to test
from main import app
from routers import secure_computations
from secure_computation_export import SecureComputationExport
from models import SecureComputation, ComputationResult, SecureComputationResult, Organization
from dependencies import get_db, require_permissions

class TestSecureComputationAPI(unittest.TestCase):
    """Integration tests for the secure computation API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a test client
        self.client = TestClient(app)
        
        # Mock the authentication dependency
        self.mock_user = {"id": 1, "username": "testuser", "permissions": ["VIEW_ANALYTICS"]}
        
        # Create a mock database session
        self.mock_db = MagicMock()
        
        # Create a mock computation
        self.mock_computation = MagicMock(spec=SecureComputation)
        self.mock_computation.computation_id = "test-comp-123"
        self.mock_computation.metric_type = "blood_pressure"
        self.mock_computation.security_method = "homomorphic"
        self.mock_computation.threshold = 3
        self.mock_computation.min_participants = 2
        self.mock_computation.status = "completed"
        self.mock_computation.created_at = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_computation.completed_at = datetime(2023, 1, 1, 12, 30, 0)
        self.mock_computation.result = {
            "aggregate": {
                "mean": 120.5,
                "median": 118.0,
                "min": 100.0,
                "max": 140.0
            }
        }
        
        # Configure the patches
        self.auth_patch = patch("routers.secure_computations.require_permissions", return_value=lambda: self.mock_user)
        self.db_patch = patch("routers.secure_computations.get_db", return_value=self.mock_db)
        
        # Start the patches
        self.mock_auth = self.auth_patch.start()
        self.mock_get_db = self.db_patch.start()
    
    def tearDown(self):
        """Clean up after tests"""
        # Stop the patches
        self.auth_patch.stop()
        self.db_patch.stop()
    
    @patch("routers.secure_computations.SecureComputationService")
    @patch("routers.secure_computations.SecureComputationExport")
    def test_export_computation_json(self, mock_export_class, mock_service_class):
        """Test exporting a computation as JSON"""
        # Configure the mocks
        mock_service = mock_service_class.return_value
        mock_service.get_computation.return_value = self.mock_computation
        
        mock_export = mock_export_class.return_value
        mock_export.export_computation_result.return_value = {
            "format": "json",
            "filename": "computation_test-comp-123_20230101_123000.json",
            "content": json.dumps({"test": "data"}),
            "content_type": "application/json"
        }
        
        # Make the request
        response = self.client.get("/secure-computations/computations/test-comp-123/export?format=json")
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(
            response.headers["Content-Disposition"],
            "attachment; filename=computation_test-comp-123_20230101_123000.json"
        )
        self.assertEqual(response.json(), {"test": "data"})
        
        # Verify the mocks were called correctly
        mock_service.get_computation.assert_called_once_with("test-comp-123")
        mock_export.export_computation_result.assert_called_once_with("test-comp-123", "json")
    
    @patch("routers.secure_computations.SecureComputationService")
    @patch("routers.secure_computations.SecureComputationExport")
    def test_export_computation_csv(self, mock_export_class, mock_service_class):
        """Test exporting a computation as CSV"""
        # Configure the mocks
        mock_service = mock_service_class.return_value
        mock_service.get_computation.return_value = self.mock_computation
        
        mock_export = mock_export_class.return_value
        mock_export.export_computation_result.return_value = {
            "format": "csv",
            "filename": "computation_test-comp-123_20230101_123000.csv",
            "content": "header1,header2\nvalue1,value2",
            "content_type": "text/csv"
        }
        
        # Make the request
        response = self.client.get("/secure-computations/computations/test-comp-123/export?format=csv")
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/csv")
        self.assertEqual(
            response.headers["Content-Disposition"],
            "attachment; filename=computation_test-comp-123_20230101_123000.csv"
        )
        self.assertEqual(response.text, "header1,header2\nvalue1,value2")
        
        # Verify the mocks were called correctly
        mock_service.get_computation.assert_called_once_with("test-comp-123")
        mock_export.export_computation_result.assert_called_once_with("test-comp-123", "csv")
    
    @patch("routers.secure_computations.SecureComputationService")
    def test_export_computation_not_found(self, mock_service_class):
        """Test exporting a computation that doesn't exist"""
        # Configure the mock to return None for the computation
        mock_service = mock_service_class.return_value
        mock_service.get_computation.return_value = None
        
        # Make the request
        response = self.client.get("/secure-computations/computations/nonexistent-id/export?format=json")
        
        # Verify the response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Computation not found"})
        
        # Verify the mock was called correctly
        mock_service.get_computation.assert_called_once_with("nonexistent-id")
    
    @patch("routers.secure_computations.SecureComputationService")
    @patch("routers.secure_computations.SecureComputationExport")
    def test_export_computation_error(self, mock_export_class, mock_service_class):
        """Test exporting a computation with an error"""
        # Configure the mocks
        mock_service = mock_service_class.return_value
        mock_service.get_computation.return_value = self.mock_computation
        
        mock_export = mock_export_class.return_value
        mock_export.export_computation_result.return_value = {
            "error": "Test error message"
        }
        
        # Make the request
        response = self.client.get("/secure-computations/computations/test-comp-123/export?format=json")
        
        # Verify the response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Test error message"})
        
        # Verify the mocks were called correctly
        mock_service.get_computation.assert_called_once_with("test-comp-123")
        mock_export.export_computation_result.assert_called_once_with("test-comp-123", "json")

if __name__ == "__main__":
    unittest.main()