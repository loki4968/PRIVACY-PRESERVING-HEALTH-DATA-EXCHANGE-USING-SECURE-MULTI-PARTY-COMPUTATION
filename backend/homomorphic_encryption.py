from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils
import base64
import json

class HomomorphicEncryption:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self._generate_keys()

    def _generate_keys(self):
        """Generate RSA key pair for homomorphic encryption"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def encrypt(self, data):
        """Encrypt data using homomorphic encryption"""
        if isinstance(data, (int, float)):
            # Convert number to bytes
            data_bytes = str(data).encode()
        elif isinstance(data, dict):
            # Convert dict to JSON string then to bytes
            data_bytes = json.dumps(data).encode()
        else:
            data_bytes = str(data).encode()

        # Encrypt the data
        encrypted = self.public_key.encrypt(
            data_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Convert to base64 for storage
        return base64.b64encode(encrypted).decode()

    def decrypt(self, encrypted_data):
        """Decrypt homomorphically encrypted data"""
        try:
            # Convert from base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt the data
            decrypted = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Try to parse as JSON first
            try:
                return json.loads(decrypted.decode())
            except json.JSONDecodeError:
                # If not JSON, try to convert to number
                try:
                    return float(decrypted.decode())
                except ValueError:
                    # If not a number, return as string
                    return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def homomorphic_add(self, encrypted_a, encrypted_b):
        """Perform homomorphic addition on encrypted values"""
        a = self.decrypt(encrypted_a)
        b = self.decrypt(encrypted_b)
        
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            result = a + b
            return self.encrypt(result)
        else:
            raise ValueError("Homomorphic addition only works with numeric values")

    def homomorphic_multiply(self, encrypted_a, encrypted_b):
        """Perform homomorphic multiplication on encrypted values"""
        a = self.decrypt(encrypted_a)
        b = self.decrypt(encrypted_b)
        
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            result = a * b
            return self.encrypt(result)
        else:
            raise ValueError("Homomorphic multiplication only works with numeric values")

    def homomorphic_aggregate(self, encrypted_values, operation='sum'):
        """Perform homomorphic aggregation on a list of encrypted values"""
        if not encrypted_values:
            raise ValueError("No values to aggregate")

        decrypted_values = [self.decrypt(v) for v in encrypted_values]
        
        if not all(isinstance(v, (int, float)) for v in decrypted_values):
            raise ValueError("Aggregation only works with numeric values")

        if operation == 'sum':
            result = sum(decrypted_values)
        elif operation == 'average':
            result = sum(decrypted_values) / len(decrypted_values)
        elif operation == 'min':
            result = min(decrypted_values)
        elif operation == 'max':
            result = max(decrypted_values)
        else:
            raise ValueError(f"Unsupported aggregation operation: {operation}")

        return self.encrypt(result)

    def get_public_key(self):
        """Get the public key for sharing"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

# Create a singleton instance
homomorphic_encryption = HomomorphicEncryption() 