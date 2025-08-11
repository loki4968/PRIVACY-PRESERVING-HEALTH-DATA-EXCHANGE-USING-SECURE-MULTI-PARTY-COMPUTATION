import base64
import hashlib
import os
from typing import Dict, Any

class EncryptionManager:
    def __init__(self):
        self.key = os.urandom(32)  # Generate a random 32-byte key
        self.salt = os.urandom(16)  # Generate a random 16-byte salt

    def _derive_key(self, password: str) -> bytes:
        """Derive a key from a password using PBKDF2"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            self.salt,
            100000,  # Number of iterations
            32  # Key length
        )

    def encrypt(self, data: str) -> str:
        """Encrypt data using a simple XOR cipher with the derived key"""
        key = self._derive_key(data)
        data_bytes = data.encode()
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key))
        return base64.b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using the same XOR cipher"""
        key = self._derive_key(encrypted_data)
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, key))
        return decrypted.decode()

    def hash_data(self, data: str) -> str:
        """Create a secure hash of the data"""
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verify if the data matches the hash"""
        return self.hash_data(data) == hash_value

class SecureComputation:
    def __init__(self):
        self.encryption_manager = EncryptionManager()

    def secure_aggregate(self, values: list, operation: str) -> Dict[str, Any]:
        """Perform secure aggregation on encrypted values"""
        if not values:
            raise ValueError("No values to aggregate")

        # Decrypt values
        decrypted_values = [float(self.encryption_manager.decrypt(v)) for v in values]

        if operation == 'average':
            return {'value': sum(decrypted_values) / len(decrypted_values)}
        elif operation == 'sum':
            return {'value': sum(decrypted_values)}
        elif operation == 'min':
            return {'value': min(decrypted_values)}
        elif operation == 'max':
            return {'value': max(decrypted_values)}
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def secure_compare(self, value1: str, value2: str) -> bool:
        """Securely compare two encrypted values"""
        decrypted1 = float(self.encryption_manager.decrypt(value1))
        decrypted2 = float(self.encryption_manager.decrypt(value2))
        return decrypted1 > decrypted2

# Utility functions for data validation
def validate_health_data(data: Dict[str, Any]) -> bool:
    """
    Validate health data before encryption.
    Returns True if data is valid, False otherwise.
    """
    print(f"Validating health data: {data}")
    
    required_fields = ["patient_id", "data_type", "timestamp"]
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")
            return False
    
    # Validate data types
    if not isinstance(data["patient_id"], str):
        print("patient_id must be a string")
        return False
    if not isinstance(data["data_type"], str):
        print("data_type must be a string")
        return False
    if not isinstance(data["timestamp"], str):
        print("timestamp must be a string")
        return False
    
    # Ensure data field exists and is a dict
    if "data" not in data or not isinstance(data["data"], dict):
        print("data field must be a dictionary")
        return False
    
    print("Health data validation passed")
    return True

def sanitize_health_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize health data before encryption.
    Removes or masks sensitive information.
    """
    print(f"Sanitizing health data: {data}")
    sanitized_data = data.copy()
    
    # Remove or mask sensitive fields
    sensitive_fields = ["ssn", "insurance_number", "phone_number"]
    for field in sensitive_fields:
        if field in sanitized_data:
            sanitized_data[field] = "REDACTED"
    
    print(f"Sanitized data: {sanitized_data}")
    return sanitized_data 