import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session

from secure_computation_audit import SecureComputationAudit
from audit import AuditLogger
from models import AuditLog, SecureComputation, User

class TestSecureComputationAudit(unittest.TestCase):
    """Unit tests for the SecureComputationAudit class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock database session
        self.mock_db = MagicMock(spec=Session)
        
        # Create a mock AuditLogger
        self.mock_audit_logger = MagicMock(spec=AuditLogger)
        
        # Initialize the audit class with mocked dependencies
        self.audit = SecureComputationAudit(self.mock_db)
        
        # Replace the audit_logger with our mock
        self.audit.audit_logger = self.mock_audit_logger
        
        # Test data
        self.user_id = 1
        self.computation_id = "test-comp-123"
        self.mock_request = MagicMock(spec=Request)
    
    def test_log_computation_initialized(self):
        """Test logging a computation initialization event"""
        # Test parameters
        metric_type = "blood_pressure"
        security_method = "standard"
        threshold = 3
        min_participants = 2
        participating_orgs = [1, 2, 3]
        
        # Call the method under test
        self.audit.log_computation_initialized(
            user_id=self.user_id,
            computation_id=self.computation_id,
            metric_type=metric_type,
            security_method=security_method,
            threshold=threshold,
            min_participants=min_participants,
            participating_orgs=participating_orgs,
            request=self.mock_request
        )
        
        # Verify the audit_logger.log_action was called with correct parameters
        self.mock_audit_logger.log_action.assert_called_once()
        call_args = self.mock_audit_logger.log_action.call_args[1]
        
        # Check the parameters
        self.assertEqual(call_args["user_id"], self.user_id)
        self.assertEqual(call_args["action"], "secure_computation_initialized")
        self.assertEqual(call_args["resource_type"], "secure_computation")
        self.assertEqual(call_args["resource_id"], self.computation_id)
        self.assertEqual(call_args["request"], self.mock_request)
        
        # Check the details dictionary
        details = call_args["details"]
        self.assertEqual(details["computation_id"], self.computation_id)
        self.assertEqual(details["metric_type"], metric_type)
        self.assertEqual(details["security_method"], security_method)
        self.assertEqual(details["threshold"], threshold)
        self.assertEqual(details["min_participants"], min_participants)
        self.assertEqual(details["participating_orgs"], participating_orgs)
        self.assertEqual(details["action_type"], "initialize")
    
    def test_log_metric_submitted(self):
        """Test logging a metric submission event"""
        # Test parameters
        value = 120.5
        
        # Call the method under test
        self.audit.log_metric_submitted(
            user_id=self.user_id,
            computation_id=self.computation_id,
            value=value,
            request=self.mock_request
        )
        
        # Verify the audit_logger.log_action was called with correct parameters
        self.mock_audit_logger.log_action.assert_called_once()
        call_args = self.mock_audit_logger.log_action.call_args[1]
        
        # Check the parameters
        self.assertEqual(call_args["user_id"], self.user_id)
        self.assertEqual(call_args["action"], "secure_computation_metric_submitted")
        self.assertEqual(call_args["resource_type"], "secure_computation")
        self.assertEqual(call_args["resource_id"], self.computation_id)
        self.assertEqual(call_args["request"], self.mock_request)
        
        # Check the details dictionary
        details = call_args["details"]
        self.assertEqual(details["computation_id"], self.computation_id)
        self.assertEqual(details["action_type"], "submit")
        # Value should not be included in the audit log for privacy reasons
        self.assertNotIn("value", details)
    
    def test_log_computation_executed(self):
        """Test logging a computation execution event"""
        # Test parameters
        status = "success"
        result_summary = {
            "organizations_count": 3,
            "data_points_count": 10,
            "computation_type": "average",
            "secure_computation_method": "standard"
        }
        
        # Call the method under test
        self.audit.log_computation_executed(
            user_id=self.user_id,
            computation_id=self.computation_id,
            status=status,
            result_summary=result_summary,
            request=self.mock_request
        )
        
        # Verify the audit_logger.log_action was called with correct parameters
        self.mock_audit_logger.log_action.assert_called_once()
        call_args = self.mock_audit_logger.log_action.call_args[1]
        
        # Check the parameters
        self.assertEqual(call_args["user_id"], self.user_id)
        self.assertEqual(call_args["action"], "secure_computation_executed")
        self.assertEqual(call_args["resource_type"], "secure_computation")
        self.assertEqual(call_args["resource_id"], self.computation_id)
        self.assertEqual(call_args["request"], self.mock_request)
        
        # Check the details dictionary
        details = call_args["details"]
        self.assertEqual(details["computation_id"], self.computation_id)
        self.assertEqual(details["status"], status)
        self.assertEqual(details["action_type"], "compute")
        
        # Check that result_summary was properly sanitized
        self.assertIn("result_summary", details)
        safe_summary = details["result_summary"]
        self.assertEqual(safe_summary["computation_completed"], True)
        self.assertEqual(safe_summary["participants_count"], 3)
        self.assertEqual(safe_summary["data_points_count"], 10)
        self.assertEqual(safe_summary["computation_type"], "average")
        self.assertEqual(safe_summary["secure_computation_method"], "standard")
    
    def test_log_computation_status_checked(self):
        """Test logging a computation status check event"""
        # Call the method under test
        self.audit.log_computation_status_checked(
            user_id=self.user_id,
            computation_id=self.computation_id,
            request=self.mock_request
        )
        
        # Verify the audit_logger.log_action was called with correct parameters
        self.mock_audit_logger.log_action.assert_called_once()
        call_args = self.mock_audit_logger.log_action.call_args[1]
        
        # Check the parameters
        self.assertEqual(call_args["user_id"], self.user_id)
        self.assertEqual(call_args["action"], "secure_computation_status_checked")
        self.assertEqual(call_args["resource_type"], "secure_computation")
        self.assertEqual(call_args["resource_id"], self.computation_id)
        self.assertEqual(call_args["request"], self.mock_request)
        
        # Check the details dictionary
        details = call_args["details"]
        self.assertEqual(details["computation_id"], self.computation_id)
        self.assertEqual(details["action_type"], "status_check")
    
    def test_log_computation_result_accessed(self):
        """Test logging a computation result access event"""
        # Call the method under test
        self.audit.log_computation_result_accessed(
            user_id=self.user_id,
            computation_id=self.computation_id,
            request=self.mock_request
        )
        
        # Verify the audit_logger.log_action was called with correct parameters
        self.mock_audit_logger.log_action.assert_called_once()
        call_args = self.mock_audit_logger.log_action.call_args[1]
        
        # Check the parameters
        self.assertEqual(call_args["user_id"], self.user_id)
        self.assertEqual(call_args["action"], "secure_computation_result_accessed")
        self.assertEqual(call_args["resource_type"], "secure_computation")
        self.assertEqual(call_args["resource_id"], self.computation_id)
        self.assertEqual(call_args["request"], self.mock_request)
        
        # Check the details dictionary
        details = call_args["details"]
        self.assertEqual(details["computation_id"], self.computation_id)
        self.assertEqual(details["action_type"], "result_access")
    
    def test_log_computation_result_exported(self):
        """Test logging a computation result export event"""
        # Test parameters
        export_format = "json"
        
        # Call the method under test
        self.audit.log_computation_result_exported(
            user_id=self.user_id,
            computation_id=self.computation_id,
            export_format=export_format,
            request=self.mock_request
        )
        
        # Verify the audit_logger.log_action was called with correct parameters
        self.mock_audit_logger.log_action.assert_called_once()
        call_args = self.mock_audit_logger.log_action.call_args[1]
        
        # Check the parameters
        self.assertEqual(call_args["user_id"], self.user_id)
        self.assertEqual(call_args["action"], "secure_computation_result_exported")
        self.assertEqual(call_args["resource_type"], "secure_computation")
        self.assertEqual(call_args["resource_id"], self.computation_id)
        self.assertEqual(call_args["request"], self.mock_request)
        
        # Check the details dictionary
        details = call_args["details"]
        self.assertEqual(details["computation_id"], self.computation_id)
        self.assertEqual(details["export_format"], export_format)
        self.assertEqual(details["action_type"], "result_export")
        

    
    def test_log_computation_error(self):
        """Test logging a computation error event"""
        # Test parameters
        error_message = "Invalid blood pressure value: 300"
        error_code = "VALIDATION_ERROR"
        
        # Call the method under test
        self.audit.log_computation_error(
            user_id=self.user_id,
            computation_id=self.computation_id,
            error_message=error_message,
            error_code=error_code,
            request=self.mock_request
        )
        
        # Verify the audit_logger.log_action was called with correct parameters
        self.mock_audit_logger.log_action.assert_called_once()
        call_args = self.mock_audit_logger.log_action.call_args[1]
        
        # Check the parameters
        self.assertEqual(call_args["user_id"], self.user_id)
        self.assertEqual(call_args["action"], "secure_computation_error")
        self.assertEqual(call_args["resource_type"], "secure_computation")
        self.assertEqual(call_args["resource_id"], self.computation_id)
        self.assertEqual(call_args["request"], self.mock_request)
        
        # Check the details dictionary
        details = call_args["details"]
        self.assertEqual(details["computation_id"], self.computation_id)
        self.assertEqual(details["error_message"], error_message)
        self.assertEqual(details["error_code"], error_code)
        self.assertEqual(details["action_type"], "error")
    

    
    def test_get_audit_logs_for_computation(self):
        """Test retrieving audit logs for a specific computation"""
        # Mock return value for get_resource_actions
        mock_logs = [
            {"action": "secure_computation_initialized", "timestamp": "2023-01-01T12:00:00"},
            {"action": "secure_computation_executed", "timestamp": "2023-01-01T12:05:00"}
        ]
        self.mock_audit_logger.get_resource_actions.return_value = mock_logs
        
        # Call the method under test
        logs = self.audit.get_audit_logs_for_computation(self.computation_id)
        
        # Verify the audit_logger.get_resource_actions was called with correct parameters
        self.mock_audit_logger.get_resource_actions.assert_called_once_with(
            resource_type="secure_computation",
            resource_id=self.computation_id
        )
        
        # Verify the result
        self.assertEqual(logs, mock_logs)
    
    def test_get_audit_logs_for_user(self):
        """Test retrieving audit logs for a specific user"""
        # Mock return value for get_user_actions
        mock_logs = [
            {"action": "secure_computation_initialized", "timestamp": "2023-01-01T12:00:00"},
            {"action": "secure_computation_executed", "timestamp": "2023-01-01T12:05:00"}
        ]
        self.mock_audit_logger.get_user_actions.return_value = mock_logs
        
        # Call the method under test
        logs = self.audit.get_audit_logs_for_user(self.user_id)
        
        # Verify the audit_logger.get_user_actions was called with correct parameters
        self.mock_audit_logger.get_user_actions.assert_called_once_with(
            user_id=self.user_id
        )
        
        # Verify the result
        self.assertEqual(logs, mock_logs)

if __name__ == "__main__":
    unittest.main()