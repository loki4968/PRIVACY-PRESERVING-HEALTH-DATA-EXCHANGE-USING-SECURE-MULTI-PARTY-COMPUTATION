from models import SecureComputation

class SecureComputationValidator:
    """Validator for secure computation metric values"""
    
    def __init__(self, db):
        """Initialize the validator with a database session
        
        Args:
            db: The database session to use for queries
        """
        self.db = db
        
    def validate_computation_request(self, request_data):
        """Validate a secure computation request
        
        Args:
            request_data: The computation request data to validate
            
        Returns:
            dict: A dictionary containing validation results with keys:
                - valid: Boolean indicating if the request is valid
                - errors: List of error messages if invalid, None otherwise
        """
        errors = []
        
        # Check required fields
        if "metric_type" not in request_data:
            errors.append("Missing required field: metric_type")
        elif not isinstance(request_data["metric_type"], str):
            errors.append("metric_type must be a string")
        elif request_data["metric_type"] not in ["blood_pressure", "blood_glucose", "heart_rate"]:
            errors.append(f"Unsupported metric type: {request_data['metric_type']}")
            
        if "participating_orgs" not in request_data:
            errors.append("Missing required field: participating_orgs")
        elif not isinstance(request_data["participating_orgs"], list):
            errors.append("participating_orgs must be a list")
        elif len(request_data["participating_orgs"]) < 2:
            errors.append("At least 2 participating organizations are required")
            
        # Check optional fields
        if "security_method" in request_data:
            if not isinstance(request_data["security_method"], str):
                errors.append("security_method must be a string")
            elif request_data["security_method"] not in ["standard", "homomorphic", "hybrid"]:
                errors.append(f"Unsupported security method: {request_data['security_method']}")
                
        if "threshold" in request_data:
            if not isinstance(request_data["threshold"], int):
                errors.append("threshold must be an integer")
            elif request_data["threshold"] < 1:
                errors.append("threshold must be at least 1")
                
        if "min_participants" in request_data:
            if not isinstance(request_data["min_participants"], int):
                errors.append("min_participants must be an integer")
            elif request_data["min_participants"] < 2:
                errors.append("min_participants must be at least 2")
                
        return {
            "valid": len(errors) == 0,
            "errors": errors if errors else None
        }
        
    def sanitize_computation_request(self, request_data):
        """Sanitize a computation request
        
        Args:
            request_data: The computation request data to sanitize
            
        Returns:
            dict: The sanitized request data
        """
        sanitized_data = {
            "metric_type": request_data["metric_type"],
            "participating_orgs": request_data["participating_orgs"],
        }
        
        # Add optional fields if present
        if "security_method" in request_data:
            sanitized_data["security_method"] = request_data["security_method"]
        else:
            sanitized_data["security_method"] = "standard"
            
        if "threshold" in request_data:
            sanitized_data["threshold"] = request_data["threshold"]
        else:
            sanitized_data["threshold"] = 2
            
        if "min_participants" in request_data:
            sanitized_data["min_participants"] = request_data["min_participants"]
        else:
            sanitized_data["min_participants"] = 3
            
        return sanitized_data
    
    def validate_metric_value(self, computation_id, value):
        """Validate a metric value for a specific computation
        
        Args:
            computation_id: The ID of the secure computation
            value: The metric value to validate
            
        Returns:
            dict: A dictionary containing validation results with keys:
                - valid: Boolean indicating if the value is valid
                - sanitized_value: The sanitized value if valid, None otherwise
                - error: Error message if invalid, None otherwise
        """
        # Get the computation from the database
        computation = self.db.query(SecureComputation).filter(
            SecureComputation.id == computation_id
        ).first()
        
        # Check if the computation exists
        if not computation:
            return {
                "valid": False,
                "sanitized_value": None,
                "error": f"Computation not found with ID: {computation_id}"
            }
        
        # Sanitize the input value
        sanitized_value = self.sanitize_input(value)
        if sanitized_value is None:
            return {
                "valid": False,
                "sanitized_value": None,
                "error": f"Invalid input value: {value}"
            }
        
        # Validate based on metric type
        metric_type = computation.metric_type
        
        if metric_type == "blood_pressure":
            return self._validate_blood_pressure(sanitized_value)
        elif metric_type == "blood_glucose":
            return self._validate_blood_glucose(sanitized_value)
        elif metric_type == "heart_rate":
            return self._validate_heart_rate(sanitized_value)
        else:
            return {
                "valid": False,
                "sanitized_value": None,
                "error": f"Unsupported metric type: {metric_type}"
            }
    
    def _validate_blood_pressure(self, value):
        """Validate a blood pressure value
        
        Args:
            value: The blood pressure value to validate
            
        Returns:
            dict: Validation result
        """
        # Blood pressure should be between 50 and 250 (systolic)
        if 50 <= value <= 250:
            return {
                "valid": True,
                "sanitized_value": value,
                "error": None
            }
        else:
            return {
                "valid": False,
                "sanitized_value": None,
                "error": f"Invalid blood pressure value: {value}. Must be between 50 and 250."
            }
    
    def _validate_blood_glucose(self, value):
        """Validate a blood glucose value
        
        Args:
            value: The blood glucose value to validate
            
        Returns:
            dict: Validation result
        """
        # Blood glucose should be between 30 and 500 mg/dL
        if 30 <= value <= 500:
            return {
                "valid": True,
                "sanitized_value": value,
                "error": None
            }
        else:
            return {
                "valid": False,
                "sanitized_value": None,
                "error": f"Invalid blood glucose value: {value}. Must be between 30 and 500."
            }
    
    def _validate_heart_rate(self, value):
        """Validate a heart rate value
        
        Args:
            value: The heart rate value to validate
            
        Returns:
            dict: Validation result
        """
        # Heart rate should be between 30 and 220 bpm
        if 30 <= value <= 220:
            return {
                "valid": True,
                "sanitized_value": value,
                "error": None
            }
        else:
            return {
                "valid": False,
                "sanitized_value": None,
                "error": f"Invalid heart rate value: {value}. Must be between 30 and 220."
            }
    
    def sanitize_input(self, value):
        """Sanitize an input value
        
        Args:
            value: The input value to sanitize
            
        Returns:
            The sanitized value (int or float) or None if invalid
        """
        # If the value is already a number, return it
        if isinstance(value, (int, float)):
            return value
        
        # If the value is a string, try to convert it to a number
        if isinstance(value, str):
            try:
                # Try to convert to int first
                return int(value)
            except ValueError:
                try:
                    # Try to convert to float
                    return float(value)
                except ValueError:
                    # Not a valid number
                    return None
        
        # For any other type, return None
        return None