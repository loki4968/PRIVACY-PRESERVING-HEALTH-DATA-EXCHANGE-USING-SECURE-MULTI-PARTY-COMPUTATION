from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Union, Dict, Any
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataEncryption:
    def __init__(self, master_key: str = None):
        """Initialize the encryption system with a master key or generate a new one."""
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = os.getenv("MASTER_KEY", Fernet.generate_key())
            if isinstance(self.master_key, str):
                self.master_key = self.master_key.encode()
        
        self.fernet = Fernet(self.master_key)

    def derive_key(self, salt: bytes, password: str) -> bytes:
        """Derive an encryption key from a password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt_data(self, data: Union[str, Dict[str, Any]], password: str = None) -> Dict[str, Any]:
        """Encrypt data with optional password protection."""
        try:
            # Convert data to JSON string if it's a dictionary
            if isinstance(data, dict):
                data = json.dumps(data)
            
            # Generate a random salt for key derivation
            salt = os.urandom(16)
            
            # If password is provided, derive a key from it
            if password:
                key = self.derive_key(salt, password)
                fernet = Fernet(key)
            else:
                fernet = self.fernet
            
            # Encrypt the data
            encrypted_data = fernet.encrypt(data.encode())
            
            # Return the encrypted data with metadata
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "salt": base64.b64encode(salt).decode(),
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt_data(self, encrypted_package: Dict[str, Any], password: str = None) -> Union[str, Dict[str, Any]]:
        """Decrypt data that was encrypted with encrypt_data."""
        try:
            # Extract the components
            encrypted_data = base64.b64decode(encrypted_package["encrypted_data"])
            salt = base64.b64decode(encrypted_package["salt"])
            
            # If password is provided, derive the key
            if password:
                key = self.derive_key(salt, password)
                fernet = Fernet(key)
            else:
                fernet = self.fernet
            
            # Decrypt the data
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            
            # Try to parse as JSON, return as string if it fails
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return decrypted_data
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def encrypt_file(self, file_path: str, password: str = None) -> Dict[str, Any]:
        """Encrypt a file and return the encrypted data package."""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Convert binary data to base64 string
            file_data_b64 = base64.b64encode(file_data).decode()
            
            # Encrypt the base64 string
            return self.encrypt_data(file_data_b64, password)
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            raise

    def decrypt_file(self, encrypted_package: Dict[str, Any], output_path: str, password: str = None) -> None:
        """Decrypt an encrypted file package and save it to the output path."""
        try:
            # Decrypt the data
            decrypted_data = self.decrypt_data(encrypted_package, password)
            
            # Convert from base64 to binary
            file_data = base64.b64decode(decrypted_data)
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(file_data)
        except Exception as e:
            logger.error(f"File decryption failed: {str(e)}")
            raise

    def rotate_key(self, new_master_key: str = None) -> str:
        """Rotate the master key and return the new key."""
        if new_master_key:
            self.master_key = new_master_key.encode()
        else:
            self.master_key = Fernet.generate_key()
        
        self.fernet = Fernet(self.master_key)
        return self.master_key.decode()

# Example usage:
# encryption = DataEncryption()
# 
# # Encrypt sensitive data
# sensitive_data = {
#     "patient_id": "12345",
#     "diagnosis": "Hypertension",
#     "medications": ["Lisinopril", "Amlodipine"]
# }
# 
# # Encrypt with password
# encrypted = encryption.encrypt_data(sensitive_data, password="secure_password")
# 
# # Decrypt with password
# decrypted = encryption.decrypt_data(encrypted, password="secure_password")
# 
# # Encrypt file
# encrypted_file = encryption.encrypt_file("patient_record.pdf", password="secure_password")
# 
# # Decrypt file
# encryption.decrypt_file(encrypted_file, "decrypted_record.pdf", password="secure_password") 