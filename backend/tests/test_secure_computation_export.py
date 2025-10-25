import unittest
import json
import csv
import io
from unittest.mock import MagicMock, patch
from datetime import datetime

# Import the modules to test
from secure_computation_export import SecureComputationExport
from models import SecureComputation, ComputationResult, SecureComputationResult, Organization

class TestSecureComputationExport(unittest.TestCase):
    """Test cases for the SecureComputationExport class"""
    
    def setUp(self):
        """Set up test fixtures"""
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
        
        # Create mock computation results
        self.mock_results = [
            MagicMock(spec=ComputationResult),
            MagicMock(spec=ComputationResult)
        ]
        self.mock_results[0].org_id = 1
        self.mock_results[0].created_at = datetime(2023, 1, 1, 12, 10, 0)
        self.mock_results[1].org_id = 2
        self.mock_results[1].created_at = datetime(2023, 1, 1, 12, 15, 0)
        
        # Create mock secure computation results
        self.mock_secure_results = [
            MagicMock(spec=SecureComputationResult),
            MagicMock(spec=SecureComputationResult)
        ]
        self.mock_secure_results[0].org_id = 1
        self.mock_secure_results[0].computation_type = "homomorphic"
        self.mock_secure_results[0].created_at = datetime(2023, 1, 1, 12, 20, 0)
        self.mock_secure_results[0].result_metadata = {"encrypted": True}
        self.mock_secure_results[0].get_result.return_value = {"aggregate_only": True, "value": 120}
        
        self.mock_secure_results[1].org_id = 2
        self.mock_secure_results[1].computation_type = "homomorphic"
        self.mock_secure_results[1].created_at = datetime(2023, 1, 1, 12, 25, 0)
        self.mock_secure_results[1].result_metadata = {"encrypted": True}
        self.mock_secure_results[1].get_result.return_value = {"aggregate_only": True, "value": 121}
        
        # Create mock organizations
        self.mock_orgs = [
            MagicMock(spec=Organization),
            MagicMock(spec=Organization)
        ]
        self.mock_orgs[0].id = 1
        self.mock_orgs[0].name = "Hospital A"
        self.mock_orgs[1].id = 2
        self.mock_orgs[1].name = "Clinic B"
        
        # Configure the mock database queries
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_computation
        self.mock_db.query.return_value.filter.return_value.all.side_effect = [
            self.mock_results,
            self.mock_secure_results,
            self.mock_orgs
        ]
        
        # Create the export service with the mock database
        self.export_service = SecureComputationExport(self.mock_db)
    
    def test_export_as_json(self):
        """Test exporting computation results as JSON"""
        # Call the export method
        result = self.export_service.export_computation_result("test-comp-123", "json")
        
        # Verify the result
        self.assertEqual(result["format"], "json")
        self.assertTrue(result["filename"].startswith("computation_test-comp-123_"))
        self.assertTrue(result["filename"].endswith(".json"))
        self.assertEqual(result["content_type"], "application/json")
        
        # Parse the JSON content
        content = json.loads(result["content"])
        
        # Verify the content structure
        self.assertIn("metadata", content)
        self.assertIn("data", content)
        
        # Verify the metadata
        self.assertIn("exported_at", content["metadata"])
        self.assertEqual(content["metadata"]["format"], "json")
        self.assertEqual(content["metadata"]["version"], "1.0")
        
        # Verify the data
        data = content["data"]
        self.assertEqual(data["computation_id"], "test-comp-123")
        self.assertEqual(data["metric_type"], "blood_pressure")
        self.assertEqual(data["security_method"], "homomorphic")
        self.assertEqual(data["threshold"], 3)
        self.assertEqual(data["min_participants"], 2)
        self.assertEqual(data["status"], "completed")
        
        # Verify participants
        self.assertEqual(len(data["participants"]), 2)
        self.assertEqual(data["participants"][0]["org_id"], 1)
        self.assertEqual(data["participants"][0]["org_name"], "Hospital A")
        self.assertEqual(data["participants"][1]["org_id"], 2)
        self.assertEqual(data["participants"][1]["org_name"], "Clinic B")
        
        # Verify results
        self.assertIn("aggregate", data["results"])
        self.assertEqual(data["results"]["aggregate"]["mean"], 120.5)
        
        # Verify secure results
        self.assertEqual(len(data["secure_results"]), 2)
        self.assertEqual(data["secure_results"][0]["org_id"], 1)
        self.assertEqual(data["secure_results"][0]["org_name"], "Hospital A")
        self.assertEqual(data["secure_results"][0]["computation_type"], "homomorphic")
        self.assertEqual(data["secure_results"][0]["result_metadata"], {"encrypted": True})
        self.assertEqual(data["secure_results"][0]["result"], {"aggregate_only": True, "value": 120})
    
    def test_export_as_csv(self):
        """Test exporting computation results as CSV"""
        # Call the export method
        result = self.export_service.export_computation_result("test-comp-123", "csv")
        
        # Verify the result
        self.assertEqual(result["format"], "csv")
        self.assertTrue(result["filename"].startswith("computation_test-comp-123_"))
        self.assertTrue(result["filename"].endswith(".csv"))
        self.assertEqual(result["content_type"], "text/csv")
        
        # Parse the CSV content
        csv_content = result["content"]
        csv_reader = csv.reader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        # Verify the header
        self.assertEqual(rows[0][0], "Secure Computation Export")
        
        # Verify computation metadata
        self.assertEqual(rows[4][0], "Computation ID")
        self.assertEqual(rows[4][1], "test-comp-123")
        self.assertEqual(rows[5][0], "Metric Type")
        self.assertEqual(rows[5][1], "blood_pressure")
        self.assertEqual(rows[6][0], "Security Method")
        self.assertEqual(rows[6][1], "homomorphic")
        
        # Verify participants section exists
        participants_header_index = None
        for i, row in enumerate(rows):
            if row and row[0] == "Participants":
                participants_header_index = i
                break
        
        self.assertIsNotNone(participants_header_index, "Participants section not found in CSV")
        
        # Verify results section exists
        results_header_index = None
        for i, row in enumerate(rows):
            if row and row[0] == "Results":
                results_header_index = i
                break
        
        self.assertIsNotNone(results_header_index, "Results section not found in CSV")
    
    def test_export_computation_not_found(self):
        """Test exporting a computation that doesn't exist"""
        # Configure the mock to return None for the computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Call the export method
        result = self.export_service.export_computation_result("nonexistent-id", "json")
        
        # Verify the result contains an error
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Computation not found")
    
    def test_export_unsupported_format(self):
        """Test exporting with an unsupported format"""
        # Call the export method with an unsupported format
        result = self.export_service.export_computation_result("test-comp-123", "pdf")
        
        # Verify the result contains an error
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Unsupported export format: pdf")

if __name__ == "__main__":
    unittest.main()