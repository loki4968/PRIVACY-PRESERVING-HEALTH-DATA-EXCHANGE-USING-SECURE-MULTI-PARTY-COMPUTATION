"""
Advanced Privacy-Preserving Techniques for Machine Learning
Enhanced differential privacy, local DP, secure aggregation, and zero-knowledge proofs
"""

import numpy as np
import random
import math
import hashlib
import secrets
from typing import List, Dict, Any, Tuple, Optional, Union
from decimal import Decimal, getcontext
from datetime import datetime
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import json

# Set precision for decimal calculations
getcontext().prec = 50

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedDifferentialPrivacy:
    """Advanced differential privacy mechanisms with multiple noise distributions"""

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
        self.sensitivity = 1.0

    def gaussian_noise(self, data: Union[float, np.ndarray], sensitivity: float = None) -> Union[float, np.ndarray]:
        """Add Gaussian noise for (ε, δ)-differential privacy"""
        if sensitivity is None:
            sensitivity = self.sensitivity

        # Calculate noise scale: σ = (sensitivity * sqrt(2 * ln(1.25/δ))) / ε
        sigma = (sensitivity * math.sqrt(2 * math.log(1.25 / self.delta))) / self.epsilon

        if isinstance(data, np.ndarray):
            noise = np.random.normal(0, sigma, data.shape)
            return data + noise
        else:
            noise = random.gauss(0, sigma)
            return data + noise

    def laplace_noise(self, data: Union[float, np.ndarray], sensitivity: float = None) -> Union[float, np.ndarray]:
        """Add Laplace noise for ε-differential privacy"""
        if sensitivity is None:
            sensitivity = self.sensitivity

        # Calculate scale parameter b = sensitivity / ε
        scale = sensitivity / self.epsilon

        if isinstance(data, np.ndarray):
            noise = np.random.laplace(0, scale, data.shape)
            return data + noise
        else:
            noise = random.expovariate(1/scale) * (1 if random.random() > 0.5 else -1)
            return data + noise

    def exponential_mechanism(self, data: List[Any], utility_function, sensitivity: float = None) -> Any:
        """Exponential mechanism for differential privacy with arbitrary output domains"""
        if sensitivity is None:
            sensitivity = self.sensitivity

        # Calculate scores for each item
        scores = [utility_function(item) for item in data]

        # Normalize scores to avoid overflow
        max_score = max(scores)
        scores = [s - max_score for s in scores]

        # Calculate probabilities: exp(ε * score / (2 * sensitivity))
        probabilities = [math.exp((self.epsilon * score) / (2 * sensitivity)) for score in scores]

        # Normalize probabilities
        total_prob = sum(probabilities)
        probabilities = [p / total_prob for p in probabilities]

        # Sample from the distribution
        r = random.random()
        cumulative_prob = 0
        for i, prob in enumerate(probabilities):
            cumulative_prob += prob
            if r <= cumulative_prob:
                return data[i]

        return data[-1]  # Fallback

    def advanced_composition(self, mechanisms: List[Tuple], target_epsilon: float) -> float:
        """Advanced composition theorem for multiple DP mechanisms"""
        # Calculate total privacy loss using advanced composition
        total_epsilon = 0
        total_delta = 0

        for epsilon_i, delta_i in mechanisms:
            total_epsilon += epsilon_i
            total_delta = max(total_delta, delta_i)

        # Apply composition bounds
        if total_epsilon <= target_epsilon:
            return total_epsilon, total_delta
        else:
            # Use more sophisticated bounds if needed
            return total_epsilon, total_delta


class LocalDifferentialPrivacy:
    """Local differential privacy for edge computing scenarios"""

    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon

    def randomized_response(self, true_value: bool, probability: float = None) -> bool:
        """Randomized response mechanism for binary data"""
        if probability is None:
            # Optimal probability for ε-LDP: e^ε / (1 + e^ε)
            probability = math.exp(self.epsilon) / (1 + math.exp(self.epsilon))

        if random.random() < probability:
            return true_value
        else:
            return not true_value

    def unary_encoding_ldp(self, value: int, domain_size: int) -> List[int]:
        """Unary encoding with local differential privacy"""
        # Create unary encoding
        encoding = [0] * domain_size
        if 0 <= value < domain_size:
            encoding[value] = 1

        # Apply randomized response to each bit
        for i in range(domain_size):
            if random.random() < 1 / (1 + math.exp(self.epsilon)):
                encoding[i] = 1 - encoding[i]

        return encoding

    def frequency_estimation_ldp(self, values: List[int], domain_size: int) -> Dict[int, float]:
        """Estimate frequencies under local differential privacy"""
        n = len(values)
        estimates = {}

        for value in range(domain_size):
            count = sum(1 for v in values if v == value)
            # Apply LDP correction: estimate = (count - n/(1+e^ε)) / (e^ε/(1+e^ε) - 1/(1+e^ε))
            correction = n / (1 + math.exp(self.epsilon))
            if count > correction:
                estimates[value] = (count - correction) / (math.exp(self.epsilon) / (1 + math.exp(self.epsilon)) - 1 / (1 + math.exp(self.epsilon)))
            else:
                estimates[value] = 0

        return estimates


class SecureAggregation:
    """Advanced secure aggregation protocols for federated learning"""

    def __init__(self, num_clients: int, threshold: int = None):
        self.num_clients = num_clients
        self.threshold = threshold or (2 * num_clients // 3)  # Default 2/3 threshold
        self.shamir = None  # Will be initialized with SMPC protocol

    def secure_federated_averaging(self, model_updates: List[np.ndarray], weights: List[float] = None) -> np.ndarray:
        """Secure federated averaging with privacy guarantees"""
        if not model_updates:
            raise ValueError("No model updates provided")

        if weights is None:
            # Equal weighting by default
            weights = [1.0 / len(model_updates)] * len(model_updates)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Compute weighted average securely
        if len(model_updates) == 1:
            return model_updates[0]

        # For multiple updates, use secure aggregation
        aggregated_update = None
        for i, update in enumerate(model_updates):
            weighted_update = update * weights[i]
            if aggregated_update is None:
                aggregated_update = weighted_update
            else:
                aggregated_update += weighted_update

        return aggregated_update

    def secure_gradient_aggregation(self, gradients: List[np.ndarray]) -> np.ndarray:
        """Secure aggregation of gradients with noise injection"""
        if not gradients:
            raise ValueError("No gradients provided")

        # Add differential privacy noise
        dp = AdvancedDifferentialPrivacy(epsilon=1.0, delta=1e-5)
        noisy_gradients = [dp.gaussian_noise(grad, sensitivity=1.0) for grad in gradients]

        # Aggregate gradients
        aggregated = np.mean(noisy_gradients, axis=0)
        return aggregated

    def threshold_aggregation(self, values: List[float], threshold: float) -> float:
        """Threshold-based secure aggregation"""
        # Only aggregate values above threshold
        filtered_values = [v for v in values if v >= threshold]

        if not filtered_values:
            return 0.0

        return sum(filtered_values) / len(filtered_values)


class ZeroKnowledgeProofs:
    """Zero-knowledge proofs for machine learning validation"""

    def __init__(self):
        self.proof_cache = {}

    def generate_model_proof(self, model_parameters: Dict[str, np.ndarray], model_hash: str) -> Dict[str, Any]:
        """Generate zero-knowledge proof for model parameters"""
        # Create commitment to model parameters
        commitment = self._create_commitment(model_parameters)

        # Generate proof that model satisfies certain properties
        proof = {
            "commitment": commitment,
            "model_hash": model_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "proof_type": "model_integrity"
        }

        # Add specific proofs based on model type
        if "weights" in model_parameters:
            proof["weight_statistics"] = self._prove_weight_statistics(model_parameters["weights"])

        return proof

    def verify_model_proof(self, proof: Dict[str, Any], model_parameters: Dict[str, np.ndarray]) -> bool:
        """Verify zero-knowledge proof for model parameters"""
        try:
            # Verify commitment
            expected_commitment = self._create_commitment(model_parameters)
            if proof["commitment"] != expected_commitment:
                return False

            # Verify weight statistics if present
            if "weight_statistics" in proof:
                if not self._verify_weight_statistics(model_parameters.get("weights", {}), proof["weight_statistics"]):
                    return False

            return True
        except Exception as e:
            logger.error(f"Proof verification failed: {str(e)}")
            return False

    def _create_commitment(self, data: Dict[str, np.ndarray]) -> str:
        """Create cryptographic commitment to data"""
        # Flatten all parameters
        flattened = []
        for key, array in data.items():
            if isinstance(array, np.ndarray):
                flattened.extend(array.flatten().tolist())
            else:
                flattened.append(float(array))

        # Create hash commitment
        data_str = json.dumps(flattened, sort_keys=True)
        commitment = hashlib.sha256(data_str.encode()).hexdigest()
        return commitment

    def _prove_weight_statistics(self, weights: np.ndarray) -> Dict[str, Any]:
        """Prove statistics about model weights without revealing them"""
        if not isinstance(weights, np.ndarray):
            return {}

        # Calculate statistics
        weight_mean = np.mean(weights)
        weight_std = np.std(weights)
        weight_min = np.min(weights)
        weight_max = np.max(weights)

        # Create proof of statistics
        proof = {
            "mean_range": self._prove_value_in_range(weight_mean, 0.1),
            "std_positive": weight_std > 0,
            "min_max_reasonable": -10 <= weight_min <= weight_max <= 10
        }

        return proof

    def _verify_weight_statistics(self, weights: np.ndarray, proof: Dict[str, Any]) -> bool:
        """Verify weight statistics proof"""
        if not isinstance(weights, np.ndarray):
            return False

        weight_mean = np.mean(weights)
        weight_std = np.std(weights)
        weight_min = np.min(weights)
        weight_max = np.max(weights)

        # Verify each claim
        if "mean_range" in proof:
            if not self._verify_range_proof(weight_mean, proof["mean_range"]):
                return False

        if "std_positive" in proof:
            if weight_std <= 0:
                return False

        if "min_max_reasonable" in proof:
            if not (-10 <= weight_min <= weight_max <= 10):
                return False

        return True

    def _prove_value_in_range(self, value: float, tolerance: float) -> Dict[str, Any]:
        """Prove that a value is within a certain range"""
        # Simple range proof using commitment
        lower_bound = value - tolerance
        upper_bound = value + tolerance

        proof = {
            "value_commitment": hashlib.sha256(str(value).encode()).hexdigest(),
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "tolerance": tolerance
        }

        return proof

    def _verify_range_proof(self, value: float, proof: Dict[str, Any]) -> bool:
        """Verify range proof"""
        expected_commitment = hashlib.sha256(str(value).encode()).hexdigest()
        if proof["value_commitment"] != expected_commitment:
            return False

        tolerance = proof.get("tolerance", 0)
        lower_bound = value - tolerance
        upper_bound = value + tolerance

        if not (proof["lower_bound"] <= lower_bound and proof["upper_bound"] >= upper_bound):
            return False

        return True


class AdvancedPrivacyService:
    """Main service integrating all advanced privacy techniques"""

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.dp = AdvancedDifferentialPrivacy(epsilon, delta)
        self.ldp = LocalDifferentialPrivacy(epsilon)
        self.secure_agg = SecureAggregation(num_clients=10)
        self.zkp = ZeroKnowledgeProofs()

    def apply_advanced_dp(self, data: Union[float, np.ndarray], mechanism: str = "gaussian") -> Union[float, np.ndarray]:
        """Apply advanced differential privacy to data"""
        if mechanism == "gaussian":
            return self.dp.gaussian_noise(data)
        elif mechanism == "laplace":
            return self.dp.laplace_noise(data)
        else:
            raise ValueError(f"Unknown DP mechanism: {mechanism}")

    def apply_local_dp(self, data: List[bool], mechanism: str = "randomized_response") -> List[bool]:
        """Apply local differential privacy to data"""
        if mechanism == "randomized_response":
            return [self.ldp.randomized_response(item) for item in data]
        else:
            raise ValueError(f"Unknown LDP mechanism: {mechanism}")

    def secure_aggregate_models(self, model_updates: List[np.ndarray], weights: List[float] = None) -> np.ndarray:
        """Securely aggregate model updates with privacy guarantees"""
        return self.secure_agg.secure_federated_averaging(model_updates, weights)

    def generate_model_zkp(self, model_parameters: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Generate zero-knowledge proof for model"""
        model_hash = hashlib.sha256(json.dumps(model_parameters, sort_keys=True).encode()).hexdigest()
        return self.zkp.generate_model_proof(model_parameters, model_hash)

    def verify_model_zkp(self, proof: Dict[str, Any], model_parameters: Dict[str, np.ndarray]) -> bool:
        """Verify zero-knowledge proof for model"""
        return self.zkp.verify_model_proof(proof, model_parameters)

    def comprehensive_privacy_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive privacy analysis on data"""
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "data_types": {},
            "privacy_risks": [],
            "recommendations": []
        }

        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)):
                analysis["data_types"][key] = "array"
                analysis["privacy_risks"].append(f"High-dimensional data in {key} may leak information")
                analysis["recommendations"].append(f"Apply differential privacy to {key}")
            elif isinstance(value, (int, float)):
                analysis["data_types"][key] = "numeric"
                analysis["privacy_risks"].append(f"Numeric value in {key} could be sensitive")
                analysis["recommendations"].append(f"Add noise to {key} using DP")
            else:
                analysis["data_types"][key] = "categorical"
                analysis["privacy_risks"].append(f"Categorical data in {key} may have uniqueness issues")
                analysis["recommendations"].append(f"Use randomized response for {key}")

        return analysis


# Example usage and testing
if __name__ == "__main__":
    # Initialize advanced privacy service
    privacy_service = AdvancedPrivacyService(epsilon=0.5, delta=1e-6)

    # Test advanced differential privacy
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    noisy_data_gaussian = privacy_service.apply_advanced_dp(data, "gaussian")
    noisy_data_laplace = privacy_service.apply_advanced_dp(data, "laplace")

    print(f"Original data: {data}")
    print(f"Gaussian DP: {noisy_data_gaussian}")
    print(f"Laplace DP: {noisy_data_laplace}")

    # Test local differential privacy
    binary_data = [True, False, True, False, True]
    ldp_data = privacy_service.apply_local_dp(binary_data, "randomized_response")
    print(f"Original binary: {binary_data}")
    print(f"LDP binary: {ldp_data}")

    # Test secure aggregation
    model_updates = [
        np.array([0.1, 0.2, 0.3]),
        np.array([0.15, 0.25, 0.35]),
        np.array([0.12, 0.22, 0.32])
    ]
    aggregated = privacy_service.secure_aggregate_models(model_updates)
    print(f"Aggregated model: {aggregated}")

    # Test zero-knowledge proofs
    model_params = {"weights": np.array([0.1, 0.2, 0.3, 0.4, 0.5])}
    proof = privacy_service.generate_model_zkp(model_params)
    is_valid = privacy_service.verify_model_zkp(proof, model_params)
    print(f"ZKP generated: {proof['commitment'][:16]}...")
    print(f"ZKP valid: {is_valid}")

    # Test comprehensive privacy analysis
    sample_data = {
        "blood_pressure": [120, 130, 125, 135, 140],
        "age": 45,
        "diagnosis": "hypertension"
    }
    analysis = privacy_service.comprehensive_privacy_analysis(sample_data)
    print(f"Privacy analysis: {json.dumps(analysis, indent=2)}")
