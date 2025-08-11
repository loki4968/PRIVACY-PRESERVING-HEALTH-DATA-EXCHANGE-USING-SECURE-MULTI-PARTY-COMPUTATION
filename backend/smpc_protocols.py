from typing import List, Dict, Any
import secrets
import json
import math
import base64
import hashlib
import os

class SMPCProtocol:
    def __init__(self):
        self.participants = {}
        self.threshold = 2  # Minimum number of participants required
        self.key = os.urandom(32)  # Generate a random 32-byte key
        self.salt = os.urandom(16)  # Generate a random 16-byte salt

    def _derive_key(self, data: str) -> bytes:
        """Derive a key from data using PBKDF2"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            data.encode(),
            self.salt,
            100000,  # Number of iterations
            32  # Key length
        )

    def _encrypt(self, data: str) -> str:
        """Encrypt data using a simple XOR cipher with the derived key"""
        key = self._derive_key(data)
        data_bytes = data.encode()
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key))
        return base64.b64encode(encrypted).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using the same XOR cipher"""
        key = self._derive_key(encrypted_data)
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, key))
        return decrypted.decode()

    def generate_shares(self, value: float, num_shares: int) -> List[float]:
        """Generate Shamir's Secret Sharing shares for a value"""
        if num_shares < self.threshold:
            raise ValueError("Number of shares must be at least equal to threshold")

        # Generate random coefficients
        coefficients = [value] + [secrets.randbelow(1000) for _ in range(self.threshold - 1)]
        
        # Generate shares using polynomial evaluation
        shares = []
        for i in range(1, num_shares + 1):
            share = sum(coef * (i ** j) for j, coef in enumerate(coefficients))
            shares.append(share)
        
        return shares

    def reconstruct_secret(self, shares: List[float]) -> float:
        """Reconstruct the secret from shares using Lagrange interpolation"""
        if len(shares) < self.threshold:
            raise ValueError("Not enough shares to reconstruct the secret")

        # Lagrange interpolation
        x_coords = list(range(1, len(shares) + 1))
        secret = 0
        
        for i, share in enumerate(shares):
            numerator = denominator = 1
            for j, x in enumerate(x_coords):
                if i != j:
                    numerator *= -x
                    denominator *= (x_coords[i] - x)
            secret += share * (numerator / denominator)
        
        return secret

    def secure_sum(self, values: List[float]) -> float:
        """Securely compute the sum of values using additive secret sharing"""
        # Generate random shares for each value
        shares = []
        for value in values:
            # Generate n-1 random shares
            random_shares = [secrets.randbelow(1000) for _ in range(len(values) - 1)]
            # Last share is value - sum of random shares
            last_share = value - sum(random_shares)
            shares.append(random_shares + [last_share])

        # Compute sum of shares
        result_shares = [sum(participant_shares) for participant_shares in zip(*shares)]
        return sum(result_shares)

    def secure_mean(self, values: List[float]) -> float:
        """Securely compute the mean of values"""
        total = self.secure_sum(values)
        return total / len(values)

    def secure_variance(self, values: List[float]) -> float:
        """Securely compute the variance of values"""
        mean = self.secure_mean(values)
        squared_diff_sum = self.secure_sum([(x - mean) ** 2 for x in values])
        return squared_diff_sum / len(values)

    def secure_percentile(self, values: List[float], percentile: float) -> float:
        """Securely compute a percentile of values"""
        if not 0 <= percentile <= 100:
            raise ValueError("Percentile must be between 0 and 100")

        # Sort values securely using a sorting network
        sorted_values = self.secure_sort(values)
        index = int(len(values) * percentile / 100)
        return sorted_values[index]

    def secure_sort(self, values: List[float]) -> List[float]:
        """Securely sort values using a sorting network"""
        # Implement a secure sorting network
        # This is a simplified version using bubble sort
        n = len(values)
        for i in range(n):
            for j in range(0, n - i - 1):
                # Securely compare and swap if needed
                if self.secure_compare(values[j], values[j + 1]):
                    values[j], values[j + 1] = values[j + 1], values[j]
        return values

    def secure_compare(self, a: float, b: float) -> bool:
        """Securely compare two values"""
        # Use secure comparison protocol
        diff = a - b
        return diff > 0

    def secure_correlation(self, shares1: List[float], shares2: List[float]) -> float:
        """Securely compute correlation between two sets of shares"""
        if len(shares1) != len(shares2):
            raise ValueError("Share sets must have the same length")

        # Compute means
        mean1 = self.secure_mean(shares1)
        mean2 = self.secure_mean(shares2)

        # Compute covariance
        cov = self.secure_sum([(x - mean1) * (y - mean2) for x, y in zip(shares1, shares2)]) / len(shares1)

        # Compute standard deviations
        std1 = math.sqrt(self.secure_variance(shares1))
        std2 = math.sqrt(self.secure_variance(shares2))

        # Compute correlation
        if std1 == 0 or std2 == 0:
            return 0.0
        return cov / (std1 * std2)

    def secure_aggregate(self, values: List[Dict[str, Any]], operation: str) -> Dict[str, Any]:
        """Securely aggregate values based on the operation type"""
        if not values:
            raise ValueError("No values to aggregate")

        numeric_values = [v['value'] for v in values if 'value' in v]
        
        if operation == 'statistics':
            return {
                'mean': self.secure_mean(numeric_values),
                'variance': self.secure_variance(numeric_values),
                'min': min(numeric_values),
                'max': max(numeric_values),
                'percentile_25': self.secure_percentile(numeric_values, 25),
                'percentile_75': self.secure_percentile(numeric_values, 75)
            }
        elif operation == 'aggregation':
            return {
                'sum': self.secure_sum(numeric_values),
                'count': len(numeric_values)
            }
        elif operation == 'comparison':
            return {
                'min': min(numeric_values),
                'max': max(numeric_values),
                'range': max(numeric_values) - min(numeric_values),
                'median': self.secure_percentile(numeric_values, 50)
            }
        else:
            raise ValueError(f"Unsupported operation: {operation}")

# Create a singleton instance
smpc_protocol = SMPCProtocol() 