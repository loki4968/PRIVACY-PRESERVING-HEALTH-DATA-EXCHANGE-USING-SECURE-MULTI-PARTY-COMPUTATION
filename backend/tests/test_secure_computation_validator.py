import unittest
from unittest.mock import MagicMock, patch

from secure_computation_validator import SecureComputationValidator
from models import SecureComputation

class TestSecureComputationValidator(unittest.TestCase):
    """Unit tests for the SecureComputationValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock database session
        self.mock_db = MagicMock()
        
        # Initialize the validator
        self.validator = SecureComputationValidator(self.mock_db)
    
    def test_validate_blood_pressure_valid(self):
        """Test validating a valid blood pressure value"""
        # Create a mock computation with blood_pressure metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "blood_pressure"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with a valid blood pressure value
        result = self.validator.validate_metric_value("test-comp-123", 120)
        
        # Verify the result
        self.assertTrue(result["valid"])
        self.assertEqual(result["sanitized_value"], 120)
        self.assertIsNone(result["error"])
    
    def test_validate_blood_pressure_invalid_low(self):
        """Test validating an invalid low blood pressure value"""
        # Create a mock computation with blood_pressure metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "blood_pressure"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with an invalid low blood pressure value
        result = self.validator.validate_metric_value("test-comp-123", 30)
        
        # Verify the result
        self.assertFalse(result["valid"])
        self.assertEqual(result["sanitized_value"], None)
        self.assertIn("Invalid blood pressure value", result["error"])
    
    def test_validate_blood_pressure_invalid_high(self):
        """Test validating an invalid high blood pressure value"""
        # Create a mock computation with blood_pressure metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "blood_pressure"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with an invalid high blood pressure value
        result = self.validator.validate_metric_value("test-comp-123", 300)
        
        # Verify the result
        self.assertFalse(result["valid"])
        self.assertEqual(result["sanitized_value"], None)
        self.assertIn("Invalid blood pressure value", result["error"])
    
    def test_validate_blood_glucose_valid(self):
        """Test validating a valid blood glucose value"""
        # Create a mock computation with blood_glucose metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "blood_glucose"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with a valid blood glucose value
        result = self.validator.validate_metric_value("test-comp-123", 100)
        
        # Verify the result
        self.assertTrue(result["valid"])
        self.assertEqual(result["sanitized_value"], 100)
        self.assertIsNone(result["error"])
    
    def test_validate_blood_glucose_invalid(self):
        """Test validating an invalid blood glucose value"""
        # Create a mock computation with blood_glucose metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "blood_glucose"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with an invalid blood glucose value
        result = self.validator.validate_metric_value("test-comp-123", 1000)
        
        # Verify the result
        self.assertFalse(result["valid"])
        self.assertEqual(result["sanitized_value"], None)
        self.assertIn("Invalid blood glucose value", result["error"])
    
    def test_validate_heart_rate_valid(self):
        """Test validating a valid heart rate value"""
        # Create a mock computation with heart_rate metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "heart_rate"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with a valid heart rate value
        result = self.validator.validate_metric_value("test-comp-123", 75)
        
        # Verify the result
        self.assertTrue(result["valid"])
        self.assertEqual(result["sanitized_value"], 75)
        self.assertIsNone(result["error"])
    
    def test_validate_heart_rate_invalid(self):
        """Test validating an invalid heart rate value"""
        # Create a mock computation with heart_rate metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "heart_rate"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with an invalid heart rate value
        result = self.validator.validate_metric_value("test-comp-123", 250)
        
        # Verify the result
        self.assertFalse(result["valid"])
        self.assertEqual(result["sanitized_value"], None)
        self.assertIn("Invalid heart rate value", result["error"])
    
    def test_validate_unknown_metric_type(self):
        """Test validating a value for an unknown metric type"""
        # Create a mock computation with an unknown metric type
        mock_computation = MagicMock(spec=SecureComputation)
        mock_computation.metric_type = "unknown_metric"
        
        # Configure the mock database to return the mock computation
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_computation
        
        # Test with any value
        result = self.validator.validate_metric_value("test-comp-123", 100)
        
        # Verify the result
        self.assertFalse(result["valid"])
        self.assertEqual(result["sanitized_value"], None)
        self.assertIn("Unsupported metric type", result["error"])
    
    def test_validate_computation_not_found(self):
        """Test validating a value for a computation that doesn't exist"""
        # Configure the mock database to return None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Test with any value
        result = self.validator.validate_metric_value("nonexistent-id", 100)
        
        # Verify the result
        self.assertFalse(result["valid"])
        self.assertEqual(result["sanitized_value"], None)
        self.assertIn("Computation not found", result["error"])
    
    def test_sanitize_input_integer(self):
        """Test sanitizing an integer input"""
        # Test with an integer
        result = self.validator.sanitize_input(100)
        
        # Verify the result
        self.assertEqual(result, 100)
    
    def test_sanitize_input_float(self):
        """Test sanitizing a float input"""
        # Test with a float
        result = self.validator.sanitize_input(100.5)
        
        # Verify the result
        self.assertEqual(result, 100.5)
    
    def test_sanitize_input_string_numeric(self):
        """Test sanitizing a numeric string input"""
        # Test with a numeric string
        result = self.validator.sanitize_input("100")
        
        # Verify the result
        self.assertEqual(result, 100)
    
    def test_sanitize_input_string_float(self):
        """Test sanitizing a float string input"""
        # Test with a float string
        result = self.validator.sanitize_input("100.5")
        
        # Verify the result
        self.assertEqual(result, 100.5)
    
    def test_sanitize_input_invalid_string(self):
        """Test sanitizing an invalid string input"""
        # Test with an invalid string
        result = self.validator.sanitize_input("not a number")
        
        # Verify the result is None
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()