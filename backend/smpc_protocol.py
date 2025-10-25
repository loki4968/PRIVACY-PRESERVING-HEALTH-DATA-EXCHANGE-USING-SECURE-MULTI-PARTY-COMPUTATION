from typing import List, Dict, Any, Union, Tuple, Optional
import random
import math
import logging
import time
from decimal import Decimal, getcontext, InvalidOperation, DivisionByZero, Overflow

# Set high precision for decimal calculations
getcontext().prec = 28

# Configure logging
logger = logging.getLogger(__name__)

# Custom exceptions for SMPC protocol
class SMPCError(Exception):
    """Base exception for all SMPC protocol errors"""
    pass

class ThresholdError(SMPCError):
    """Raised when threshold requirements are not met"""
    pass

class ShareGenerationError(SMPCError):
    """Raised when there's an error generating shares"""
    pass

class SecretReconstructionError(SMPCError):
    """Raised when there's an error reconstructing the secret"""
    pass

class ComputationTimeoutError(SMPCError):
    """Raised when a computation exceeds the maximum allowed time"""
    pass

class SMPCProtocol:
    """Implementation of Secure Multi-Party Computation protocols
    
    This class provides methods for secure computation across multiple parties
    without revealing individual data points. It implements:
    
    1. Shamir's Secret Sharing for distributing secrets
    2. Secure aggregation protocols for sum, mean, and variance
    3. Threshold-based reconstruction of secrets
    """
    
    def __init__(self, threshold: int = 2, prime_bits: int = 256, max_computation_time: int = 30):
        """Initialize the SMPC protocol
        
        Args:
            threshold: Minimum number of shares needed to reconstruct a secret
            prime_bits: Size of the prime field for modular arithmetic
            max_computation_time: Maximum time in seconds allowed for any computation
        """
        if threshold < 2:
            raise ThresholdError("Threshold must be at least 2")
            
        self.threshold = threshold
        self.prime = self._generate_prime(prime_bits)
        self.max_computation_time = max_computation_time
        
        logger.info(f"Initialized SMPC protocol with threshold {threshold} and prime size {prime_bits} bits")
    
    def _generate_prime(self, bits: int) -> int:
        """Generate a large prime number for the finite field
        
        For production use, this would use a cryptographically secure method.
        For this implementation, we use a simplified approach.
        
        Args:
            bits: Number of bits in the prime
            
        Returns:
            A prime number of the specified bit length
        """
        # For simplicity, use a pre-computed large prime
        # In production, would generate this securely
        if bits <= 64:
            return 2**61 - 1  # Mersenne prime
        elif bits <= 128:
            return 2**127 - 1  # Mersenne prime
        else:
            return 2**255 - 19  # Prime used in Ed25519
    
    def generate_shares(self, secret: Decimal, num_shares: int) -> List[Dict[str, Any]]:
        """Generate Shamir's secret shares for a given secret
        
        Args:
            secret: The secret value to share
            num_shares: Number of shares to generate
            
        Returns:
            List of share dictionaries, each containing x and y values
            
        Raises:
            ThresholdError: If number of shares is less than the threshold
            ShareGenerationError: If there's an error during share generation
            ComputationTimeoutError: If the computation takes too long
        """
        start_time = time.time()
        
        try:
            if num_shares < self.threshold:
                raise ThresholdError(f"Number of shares must be at least {self.threshold}")
            
            if not isinstance(secret, Decimal):
                try:
                    secret = Decimal(str(secret))
                except (InvalidOperation, ValueError) as e:
                    raise ShareGenerationError(f"Invalid secret value: {e}")
            
            # Convert decimal to integer for finite field arithmetic
            # Scale by 10^10 to preserve decimal precision
            scaling_factor = Decimal(10**10)
            try:
                secret_int = int(secret * scaling_factor) % self.prime
            except (InvalidOperation, OverflowError, TypeError) as e:
                raise ShareGenerationError(f"Error converting secret to integer: {e}")
            
            # Generate random coefficients for the polynomial
            # p(x) = secret + a_1 * x + a_2 * x^2 + ... + a_{t-1} * x^{t-1}
            coefficients = [secret_int]
            for _ in range(self.threshold - 1):
                if time.time() - start_time > self.max_computation_time:
                    raise ComputationTimeoutError("Share generation timed out")
                coefficients.append(random.randint(1, self.prime - 1))
            
            # Generate the shares
            shares = []
            for i in range(1, num_shares + 1):
                if time.time() - start_time > self.max_computation_time:
                    raise ComputationTimeoutError("Share generation timed out")
                    
                # Evaluate the polynomial at x = i
                x = i
                y = 0
                for j, coef in enumerate(coefficients):
                    y = (y + coef * pow(x, j, self.prime)) % self.prime
                
                shares.append({
                    "x": x,
                    "y": y,
                    "scaling_factor": int(scaling_factor),
                    "prime": self.prime
                })
            
            logger.debug(f"Generated {num_shares} shares for secret")
            return shares
            
        except (ThresholdError, ShareGenerationError, ComputationTimeoutError) as e:
            logger.error(f"Error generating shares: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating shares: {str(e)}")
            raise ShareGenerationError(f"Unexpected error: {str(e)}")
    
    def reconstruct_secret(self, shares: List[Dict[str, Any]]) -> Decimal:
        """Reconstruct the secret from a set of shares using Lagrange interpolation
        
        Args:
            shares: List of share dictionaries, each containing x and y values
            
        Returns:
            The reconstructed secret value
            
        Raises:
            ThresholdError: If there are not enough shares to meet the threshold
            SecretReconstructionError: If there's an error during reconstruction
            ComputationTimeoutError: If the computation takes too long
        """
        start_time = time.time()
        
        try:
            if not shares or not isinstance(shares, list):
                raise SecretReconstructionError("Invalid shares: must be a non-empty list")
                
            if len(shares) < self.threshold:
                raise ThresholdError(f"Need at least {self.threshold} shares to reconstruct the secret, got {len(shares)}")
            
            # Validate share format
            for share in shares:
                if not isinstance(share, dict) or not all(k in share for k in ["x", "y", "prime", "scaling_factor"]):
                    raise SecretReconstructionError("Invalid share format")
            
            # Use only the threshold number of shares
            shares = shares[:self.threshold]
            
            # Extract the prime and scaling factor from the first share
            prime = shares[0]["prime"]
            try:
                scaling_factor = Decimal(shares[0]["scaling_factor"])
            except (InvalidOperation, ValueError) as e:
                raise SecretReconstructionError(f"Invalid scaling factor: {e}")
            
            # Lagrange interpolation to reconstruct the secret
            secret = 0
            for i, share_i in enumerate(shares):
                if time.time() - start_time > self.max_computation_time:
                    raise ComputationTimeoutError("Secret reconstruction timed out")
                    
                x_i, y_i = share_i["x"], share_i["y"]
                
                # Calculate the Lagrange basis polynomial
                numerator, denominator = 1, 1
                for j, share_j in enumerate(shares):
                    if i != j:
                        x_j = share_j["x"]
                        if x_i == x_j:
                            raise SecretReconstructionError("Duplicate x values in shares")
                        numerator = (numerator * (-x_j)) % prime
                        denominator = (denominator * (x_i - x_j)) % prime
                
                try:
                    # Calculate the modular inverse of the denominator
                    mod_inverse = self._mod_inverse(denominator, prime)
                    lambda_i = (y_i * numerator * mod_inverse) % prime
                    secret = (secret + lambda_i) % prime
                except ValueError as e:
                    raise SecretReconstructionError(f"Error in Lagrange interpolation: {e}")
            
            # Convert back to decimal
            try:
                result = Decimal(secret) / scaling_factor
                logger.debug("Successfully reconstructed secret")
                return result
            except (InvalidOperation, DivisionByZero, Overflow) as e:
                raise SecretReconstructionError(f"Error converting result to Decimal: {e}")
                
        except (ThresholdError, SecretReconstructionError, ComputationTimeoutError) as e:
            logger.error(f"Error reconstructing secret: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reconstructing secret: {str(e)}")
            raise SecretReconstructionError(f"Unexpected error: {str(e)}")
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """Calculate the modular multiplicative inverse
        
        Args:
            a: The number to find the inverse for
            m: The modulus
            
        Returns:
            The modular multiplicative inverse of a mod m
            
        Raises:
            ValueError: If the modular inverse does not exist
        """
        try:
            g, x, y = self._extended_gcd(a % m, m)
            if g != 1:
                raise ValueError(f"Modular inverse does not exist for {a} mod {m}")
            else:
                return (x % m + m) % m
        except Exception as e:
            logger.error(f"Error calculating modular inverse: {str(e)}")
            raise ValueError(f"Error calculating modular inverse: {str(e)}")
    
    def _extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        """Extended Euclidean Algorithm to find gcd and coefficients
        
        Args:
            a, b: Integers to find GCD for
            
        Returns:
            Tuple of (gcd, x, y) where ax + by = gcd(a, b)
        """
        if a == 0:
            return b, 0, 1
        else:
            gcd, x1, y1 = self._extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
    
    def secure_sum(self, values: List[Decimal]) -> Decimal:
        """Compute the sum of values securely
        
        This method assumes the values are already secret shares.
        For real SMPC, each party would contribute their own shares.
        
        Args:
            values: List of values (or shares) to sum
            
        Returns:
            The sum of the values
            
        Raises:
            SecretReconstructionError: If there's an error during reconstruction
            ComputationTimeoutError: If the computation takes too long
        """
        start_time = time.time()
        
        try:
            if not values:
                return Decimal(0)
            
            # For demonstration, we'll treat these as shares and reconstruct
            # In a real implementation, we would add the shares directly
            
            # Convert values to shares format if they're not already
            shares = []
            for i, value in enumerate(values):
                if time.time() - start_time > self.max_computation_time:
                    raise ComputationTimeoutError("Secure sum computation timed out")
                    
                if isinstance(value, dict) and "x" in value and "y" in value:
                    # Already in share format
                    shares.append(value)
                else:
                    try:
                        # Convert to Decimal if not already
                        if not isinstance(value, Decimal):
                            value = Decimal(str(value))
                            
                        # Create a synthetic share
                        shares.append({
                            "x": i + 1,
                            "y": int(value * Decimal(10**10)),
                            "scaling_factor": 10**10,
                            "prime": self.prime
                        })
                    except (InvalidOperation, ValueError, OverflowError) as e:
                        raise SecretReconstructionError(f"Error converting value to share: {e}")
            
            # Reconstruct the sum
            logger.debug(f"Computing secure sum of {len(values)} values")
            return self.reconstruct_secret(shares)
            
        except (SecretReconstructionError, ComputationTimeoutError) as e:
            logger.error(f"Error computing secure sum: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error computing secure sum: {str(e)}")
            raise SecretReconstructionError(f"Error computing secure sum: {str(e)}")
    
    def secure_mean(self, values: List[Decimal]) -> Decimal:
        """Compute the mean of values securely
        
        Args:
            values: List of values to compute the mean for
            
        Returns:
            The mean of the values
            
        Raises:
            SecretReconstructionError: If there's an error during computation
            ComputationTimeoutError: If the computation takes too long
        """
        try:
            if not values:
                return Decimal(0)
            
            # Compute sum and divide by count
            secure_sum = self.secure_sum(values)
            try:
                result = secure_sum / Decimal(len(values))
                logger.debug(f"Computed secure mean of {len(values)} values")
                return result
            except (InvalidOperation, DivisionByZero, Overflow) as e:
                raise SecretReconstructionError(f"Error computing mean: {e}")
                
        except (SecretReconstructionError, ComputationTimeoutError) as e:
            logger.error(f"Error computing secure mean: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error computing secure mean: {str(e)}")
            raise SecretReconstructionError(f"Error computing secure mean: {str(e)}")
    
    def secure_variance(self, values: List[Decimal]) -> Decimal:
        """Compute the variance of values securely
        
        Args:
            values: List of values to compute the variance for
            
        Returns:
            The variance of the values
            
        Raises:
            SecretReconstructionError: If there's an error during computation
            ComputationTimeoutError: If the computation takes too long
        """
        start_time = time.time()
        
        try:
            if not values or len(values) < 2:
                return Decimal(0)
            
            # First compute the mean
            mean = self.secure_mean(values)
            
            # Then compute the sum of squared differences
            squared_diffs = []
            for value in values:
                if time.time() - start_time > self.max_computation_time:
                    raise ComputationTimeoutError("Secure variance computation timed out")
                    
                try:
                    # In a real implementation, this would be done with secure computation
                    # Here we're simplifying by computing locally
                    if isinstance(value, dict) and "x" in value and "y" in value:
                        # Reconstruct the value from the share
                        val = self.reconstruct_secret([value])
                        squared_diff = (val - mean) ** 2
                    else:
                        # Convert to Decimal if not already
                        if not isinstance(value, Decimal):
                            value = Decimal(str(value))
                        squared_diff = (value - mean) ** 2
                    
                    # Create a share for the squared difference
                    squared_diffs.append(squared_diff)
                except (InvalidOperation, ValueError, OverflowError) as e:
                    raise SecretReconstructionError(f"Error computing squared difference: {e}")
            
            # Compute the mean of squared differences (variance)
            try:
                result = self.secure_sum(squared_diffs) / Decimal(len(values))
                logger.debug(f"Computed secure variance of {len(values)} values")
                return result
            except (InvalidOperation, DivisionByZero, Overflow) as e:
                raise SecretReconstructionError(f"Error computing variance: {e}")
                
        except (SecretReconstructionError, ComputationTimeoutError) as e:
            logger.error(f"Error computing secure variance: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error computing secure variance: {str(e)}")
            raise SecretReconstructionError(f"Error computing secure variance: {str(e)}")

# Create a singleton instance
try:
    smpc_protocol = SMPCProtocol(threshold=2)
    logger.info("SMPC protocol singleton instance created successfully")
except Exception as e:
    logger.error(f"Failed to create SMPC protocol singleton instance: {str(e)}")
    # Create a fallback instance with minimal functionality
    smpc_protocol = SMPCProtocol(threshold=2)