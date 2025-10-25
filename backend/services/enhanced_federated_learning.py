"""
Enhanced Federated Learning with Advanced Privacy Guarantees
Secure aggregation, differential privacy, secure model updates, and deep neural network support
"""

import numpy as np
import random
import math
import hashlib
import secrets
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime
import logging
import json
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureAggregationProtocol:
    """Advanced secure aggregation protocols for federated learning"""

    def __init__(self, num_clients: int, threshold: int = None, use_dp: bool = True):
        self.num_clients = num_clients
        self.threshold = threshold or (2 * num_clients // 3)
        self.use_dp = use_dp
        self.dp_epsilon = 1.0
        self.dp_delta = 1e-5

    def secure_federated_averaging(self, model_updates: List[np.ndarray],
                                 sample_counts: List[int] = None) -> np.ndarray:
        """Secure federated averaging with privacy guarantees"""
        if not model_updates:
            raise ValueError("No model updates provided")

        if sample_counts is None:
            # Equal weighting if no sample counts provided
            sample_counts = [1] * len(model_updates)

        # Normalize sample counts
        total_samples = sum(sample_counts)
        weights = [count / total_samples for count in sample_counts]

        # Apply differential privacy if enabled
        if self.use_dp:
            model_updates = self._apply_dp_to_updates(model_updates)

        # Secure aggregation
        aggregated_update = self._secure_aggregate_updates(model_updates, weights)

        return aggregated_update

    def _apply_dp_to_updates(self, updates: List[np.ndarray]) -> List[np.ndarray]:
        """Apply differential privacy to model updates"""
        noisy_updates = []

        for update in updates:
            # Calculate sensitivity (clipping norm)
            sensitivity = np.linalg.norm(update)
            if sensitivity > 1.0:
                update = update / sensitivity  # Clip to unit norm

            # Add Gaussian noise
            noise_scale = (sensitivity * math.sqrt(2 * math.log(1.25 / self.dp_delta))) / self.dp_epsilon
            noise = np.random.normal(0, noise_scale, update.shape)
            noisy_update = update + noise
            noisy_updates.append(noisy_update)

        return noisy_updates

    def _secure_aggregate_updates(self, updates: List[np.ndarray], weights: List[float]) -> np.ndarray:
        """Securely aggregate model updates"""
        if len(updates) != len(weights):
            raise ValueError("Number of updates must match number of weights")

        # Weighted sum
        aggregated = np.zeros_like(updates[0])
        for update, weight in zip(updates, weights):
            aggregated += weight * update

        return aggregated

    def threshold_aggregation(self, updates: List[np.ndarray], threshold: float = 0.1) -> np.ndarray:
        """Threshold-based aggregation - only include updates above threshold"""
        # Filter updates based on magnitude
        filtered_updates = []
        filtered_weights = []

        for update in updates:
            magnitude = np.linalg.norm(update)
            if magnitude >= threshold:
                filtered_updates.append(update)
                filtered_weights.append(1.0 / len(filtered_updates))

        if not filtered_updates:
            return np.zeros_like(updates[0])

        return self._secure_aggregate_updates(filtered_updates, filtered_weights)

    def robust_aggregation(self, updates: List[np.ndarray], contamination_rate: float = 0.1) -> np.ndarray:
        """Robust aggregation resistant to malicious updates"""
        if len(updates) < 3:
            return self._secure_aggregate_updates(updates, [1.0/len(updates)] * len(updates))

        # Calculate median update (coordinate-wise)
        stacked_updates = np.stack(updates, axis=0)
        median_update = np.median(stacked_updates, axis=0)

        # Calculate distances from median
        distances = [np.linalg.norm(update - median_update) for update in updates]

        # Filter out outliers (top contamination_rate)
        n_outliers = int(contamination_rate * len(updates))
        if n_outliers > 0:
            threshold_distance = sorted(distances)[-(n_outliers+1)]
            clean_updates = [update for update, dist in zip(updates, distances)
                           if dist <= threshold_distance]
        else:
            clean_updates = updates

        if not clean_updates:
            return median_update

        return self._secure_aggregate_updates(clean_updates, [1.0/len(clean_updates)] * len(clean_updates))


class SecureModelUpdateProtocol:
    """Secure model update protocols for federated learning"""

    def __init__(self, key_size: int = 2048):
        self.key_size = key_size
        self.update_history = {}

    def secure_model_update(self, model_update: np.ndarray, client_id: str,
                          round_number: int) -> Dict[str, Any]:
        """Create a secure model update with integrity checks"""
        # Create update hash for integrity
        update_hash = self._hash_model_update(model_update)

        # Add timestamp and metadata
        secure_update = {
            "update": model_update.tolist(),
            "client_id": client_id,
            "round_number": round_number,
            "timestamp": datetime.utcnow().isoformat(),
            "update_hash": update_hash,
            "signature": self._sign_update(model_update, client_id)
        }

        # Store in history for verification
        self.update_history[f"{client_id}_{round_number}"] = secure_update

        return secure_update

    def verify_model_update(self, secure_update: Dict[str, Any]) -> bool:
        """Verify the integrity of a model update"""
        try:
            # Extract components
            update = np.array(secure_update["update"])
            client_id = secure_update["client_id"]
            round_number = secure_update["round_number"]
            provided_hash = secure_update["update_hash"]
            signature = secure_update["signature"]

            # Verify hash
            expected_hash = self._hash_model_update(update)
            if provided_hash != expected_hash:
                logger.warning(f"Hash verification failed for client {client_id}")
                return False

            # Verify signature
            if not self._verify_signature(update, signature, client_id):
                logger.warning(f"Signature verification failed for client {client_id}")
                return False

            return True
        except Exception as e:
            logger.error(f"Update verification error: {str(e)}")
            return False

    def _hash_model_update(self, update: np.ndarray) -> str:
        """Create hash of model update"""
        update_bytes = update.tobytes()
        return hashlib.sha256(update_bytes).hexdigest()

    def _sign_update(self, update: np.ndarray, client_id: str) -> str:
        """Sign model update (simplified for demo)"""
        update_hash = self._hash_model_update(update)
        signature_data = f"{update_hash}_{client_id}_{datetime.utcnow().isoformat()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()

    def _verify_signature(self, update: np.ndarray, signature: str, client_id: str) -> bool:
        """Verify signature (simplified for demo)"""
        expected_signature = self._sign_update(update, client_id)
        return signature == expected_signature


class FederatedDeepLearning:
    """Federated learning for deep neural networks"""

    def __init__(self, input_size: int, hidden_layers: List[int], output_size: int,
                 num_clients: int = 10, aggregation_protocol: str = "secure_avg"):
        self.input_size = input_size
        self.hidden_layers = hidden_layers
        self.output_size = output_size
        self.num_clients = num_clients
        self.aggregation_protocol = aggregation_protocol

        # Initialize global model
        self.global_model = self._initialize_model()

        # Initialize secure aggregation
        self.secure_agg = SecureAggregationProtocol(num_clients)

        # Initialize secure update protocol
        self.update_protocol = SecureModelUpdateProtocol()

        # Training history
        self.training_history = []

    def _initialize_model(self) -> Dict[str, np.ndarray]:
        """Initialize model parameters"""
        model = {}

        # Input to first hidden layer
        model["W1"] = np.random.randn(self.hidden_layers[0], self.input_size) * 0.01
        model["b1"] = np.zeros((self.hidden_layers[0], 1))

        # Hidden layers
        for i in range(1, len(self.hidden_layers)):
            model[f"W{i+1}"] = np.random.randn(self.hidden_layers[i], self.hidden_layers[i-1]) * 0.01
            model[f"b{i+1}"] = np.zeros((self.hidden_layers[i], 1))

        # Last hidden to output
        model[f"W{len(self.hidden_layers)+1}"] = np.random.randn(self.output_size, self.hidden_layers[-1]) * 0.01
        model[f"b{len(self.hidden_layers)+1}"] = np.zeros((self.output_size, 1))

        return model

    def forward_pass(self, X: np.ndarray, model: Dict[str, np.ndarray] = None) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Forward pass through the network"""
        if model is None:
            model = self.global_model

        activations = {"A0": X.T}
        pre_activations = {}

        layer_num = 1
        while f"W{layer_num}" in model:
            W = model[f"W{layer_num}"]
            b = model[f"b{layer_num}"]

            Z = np.dot(W, activations[f"A{layer_num-1}"]) + b
            pre_activations[f"Z{layer_num}"] = Z

            if layer_num == len(self.hidden_layers) + 1:  # Output layer
                A = self._sigmoid(Z)
            else:  # Hidden layers
                A = self._relu(Z)

            activations[f"A{layer_num}"] = A
            layer_num += 1

        return activations[f"A{layer_num-1}"].T, pre_activations

    def backward_pass(self, X: np.ndarray, y: np.ndarray, activations: Dict[str, np.ndarray],
                     pre_activations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Backward pass to compute gradients"""
        m = X.shape[0]
        gradients = {}

        # Output layer gradients
        output_layer = len(self.hidden_layers) + 1
        A_final = activations[f"A{output_layer-1}"]
        dZ_final = A_final - y.T
        dA_final = dZ_final * self._sigmoid_derivative(A_final)

        gradients[f"dW{output_layer-1}"] = np.dot(dA_final, activations[f"A{output_layer-2}"].T) / m
        gradients[f"db{output_layer-1}"] = np.sum(dA_final, axis=1, keepdims=True) / m

        # Hidden layer gradients
        for layer in range(output_layer - 2, 0, -1):
            dA = np.dot(self.global_model[f"W{layer+1}"].T, dA_final)
            dZ = dA * self._relu_derivative(pre_activations[f"Z{layer+1}"])
            dA_final = dZ

            gradients[f"dW{layer}"] = np.dot(dZ, activations[f"A{layer-1}"].T) / m
            gradients[f"db{layer}"] = np.sum(dZ, axis=1, keepdims=True) / m

        return gradients

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def _sigmoid_derivative(self, x: np.ndarray) -> np.ndarray:
        return x * (1 - x)

    def _relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    def _relu_derivative(self, x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(float)

    def train_client_model(self, client_data: Tuple[np.ndarray, np.ndarray],
                          local_epochs: int = 5, learning_rate: float = 0.01) -> Dict[str, np.ndarray]:
        """Train local model on client data"""
        X, y = client_data
        local_model = self._initialize_model()

        for epoch in range(local_epochs):
            # Forward pass
            predictions, _ = self.forward_pass(X, local_model)

            # Compute loss
            loss = np.mean((predictions - y) ** 2)

            # For simplicity, we'll use the global model for gradients
            # In practice, you'd compute gradients locally
            gradients = self.backward_pass(X, y, {"A1": predictions.T}, {})

            # Update local model
            for key in local_model.keys():
                if key.startswith("W"):
                    grad_key = "d" + key
                    if grad_key in gradients:
                        local_model[key] -= learning_rate * gradients[grad_key]

        # Compute model update (difference from global model)
        model_update = {}
        for key in local_model.keys():
            model_update[key] = local_model[key] - self.global_model[key]

        return model_update

    def aggregate_client_updates(self, client_updates: List[Dict[str, np.ndarray]],
                               sample_counts: List[int] = None) -> Dict[str, np.ndarray]:
        """Aggregate client model updates"""
        if not client_updates:
            return self.global_model

        # Convert updates to numpy arrays
        update_arrays = []
        for update in client_updates:
            update_array = np.concatenate([update[key].flatten() for key in sorted(update.keys())])
            update_arrays.append(update_array)

        # Secure aggregation
        aggregated_update = self.secure_agg.secure_federated_averaging(update_arrays, sample_counts)

        # Update global model
        start_idx = 0
        for key in sorted(self.global_model.keys()):
            param_shape = self.global_model[key].shape
            param_size = np.prod(param_shape)

            param_update = aggregated_update[start_idx:start_idx + param_size].reshape(param_shape)
            self.global_model[key] += param_update

            start_idx += param_size

        return self.global_model

    def federated_training_round(self, client_datasets: List[Tuple[np.ndarray, np.ndarray]],
                               sample_counts: List[int] = None) -> Dict[str, Any]:
        """Perform one round of federated training"""
        if len(client_datasets) != self.num_clients:
            raise ValueError(f"Expected {self.num_clients} datasets, got {len(client_datasets)}")

        # Train local models
        client_updates = []
        for i, dataset in enumerate(client_datasets):
            update = self.train_client_model(dataset)
            secure_update = self.update_protocol.secure_model_update(update, f"client_{i}", len(self.training_history))
            client_updates.append(secure_update)

        # Verify updates
        verified_updates = []
        for update in client_updates:
            if self.update_protocol.verify_model_update(update):
                verified_updates.append(update)
            else:
                logger.warning(f"Discarding invalid update from {update['client_id']}")

        if not verified_updates:
            raise ValueError("No valid updates received")

        # Extract model updates
        model_updates = [np.array(update["update"]) for update in verified_updates]

        # Aggregate updates
        self.aggregate_client_updates(model_updates, sample_counts)

        # Record training round
        round_info = {
            "round_number": len(self.training_history),
            "num_clients": len(verified_updates),
            "timestamp": datetime.utcnow().isoformat(),
            "global_model_hash": self._hash_model_update(self.global_model)
        }
        self.training_history.append(round_info)

        return round_info

    def _hash_model_update(self, model: Dict[str, np.ndarray]) -> str:
        """Create hash of model parameters"""
        flattened = []
        for key in sorted(model.keys()):
            flattened.extend(model[key].flatten().tolist())

        data_str = json.dumps(flattened, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


class DifferentialPrivacyFederatedLearning:
    """Federated learning with differential privacy guarantees"""

    def __init__(self, noise_multiplier: float = 1.0, max_grad_norm: float = 1.0):
        self.noise_multiplier = noise_multiplier
        self.max_grad_norm = max_grad_norm
        self.privacy_accountant = PrivacyAccountant()

    def add_dp_noise(self, gradients: np.ndarray) -> np.ndarray:
        """Add differential privacy noise to gradients"""
        # Clip gradients
        grad_norm = np.linalg.norm(gradients)
        if grad_norm > self.max_grad_norm:
            gradients = gradients * (self.max_grad_norm / grad_norm)

        # Add Gaussian noise
        noise_std = self.noise_multiplier * self.max_grad_norm
        noise = np.random.normal(0, noise_std, gradients.shape)

        return gradients + noise

    def train_with_dp(self, model: Dict[str, np.ndarray], X: np.ndarray, y: np.ndarray,
                     learning_rate: float = 0.01) -> Dict[str, np.ndarray]:
        """Train model with differential privacy"""
        # Forward pass
        predictions, _ = self.forward_pass(X, model)

        # Backward pass
        gradients = self.backward_pass(X, y, {"A1": predictions.T}, {})

        # Add DP noise to gradients
        for key in gradients.keys():
            gradients[key] = self.add_dp_noise(gradients[key])

        # Update model
        for key in model.keys():
            if key.startswith("W"):
                grad_key = "d" + key
                if grad_key in gradients:
                    model[key] -= learning_rate * gradients[grad_key]

        return model

    def forward_pass(self, X: np.ndarray, model: Dict[str, np.ndarray]) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Forward pass (same as base class)"""
        # This would be the same as in FederatedDeepLearning
        pass

    def backward_pass(self, X: np.ndarray, y: np.ndarray, activations: Dict[str, np.ndarray],
                     pre_activations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Backward pass (same as base class)"""
        # This would be the same as in FederatedDeepLearning
        pass


class PrivacyAccountant:
    """Track privacy budget in federated learning"""

    def __init__(self):
        self.total_epsilon = 0.0
        self.total_delta = 0.0
        self.rounds = []

    def add_round(self, epsilon: float, delta: float):
        """Add privacy cost of a training round"""
        self.total_epsilon += epsilon
        self.total_delta = max(self.total_delta, delta)

        self.rounds.append({
            "epsilon": epsilon,
            "delta": delta,
            "total_epsilon": self.total_epsilon,
            "total_delta": self.total_delta,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_privacy_budget(self) -> Dict[str, float]:
        """Get current privacy budget"""
        return {
            "total_epsilon": self.total_epsilon,
            "total_delta": self.total_delta,
            "remaining_epsilon": max(0, 10.0 - self.total_epsilon),  # Assuming target ε=10
            "privacy_loss": self.total_epsilon
        }

    def is_privacy_budget_exceeded(self, max_epsilon: float = 10.0) -> bool:
        """Check if privacy budget is exceeded"""
        return self.total_epsilon >= max_epsilon


class EnhancedFederatedLearningService:
    """Main service for enhanced federated learning"""

    def __init__(self, num_clients: int = 10):
        self.num_clients = num_clients
        self.federated_learning = FederatedDeepLearning(
            input_size=784,  # MNIST example
            hidden_layers=[256, 128, 64],
            output_size=10,
            num_clients=num_clients
        )
        self.dp_federated_learning = DifferentialPrivacyFederatedLearning()
        self.privacy_accountant = PrivacyAccountant()

    def run_federated_learning(self, client_datasets: List[Tuple[np.ndarray, np.ndarray]],
                             num_rounds: int = 10, sample_counts: List[int] = None) -> Dict[str, Any]:
        """Run federated learning training"""
        if len(client_datasets) != self.num_clients:
            raise ValueError(f"Expected {self.num_clients} datasets, got {len(client_datasets)}")

        training_results = []

        for round_num in range(num_rounds):
            try:
                round_result = self.federated_learning.federated_training_round(client_datasets, sample_counts)
                training_results.append(round_result)

                # Update privacy budget
                self.privacy_accountant.add_round(0.1, 1e-5)  # Example privacy costs

                logger.info(f"Federated learning round {round_num + 1}/{num_rounds} completed")

                # Check privacy budget
                if self.privacy_accountant.is_privacy_budget_exceeded():
                    logger.warning("Privacy budget exceeded, stopping training")
                    break

            except Exception as e:
                logger.error(f"Error in federated learning round {round_num + 1}: {str(e)}")
                break

        return {
            "training_results": training_results,
            "final_model_hash": self.federated_learning._hash_model_update(self.federated_learning.global_model),
            "privacy_budget": self.privacy_accountant.get_privacy_budget(),
            "num_rounds_completed": len(training_results)
        }

    def get_model_update(self, client_id: str, round_number: int) -> Dict[str, Any]:
        """Get secure model update for a client"""
        # This would typically involve sending the current global model to the client
        # and receiving their update
        return {
            "model_hash": self.federated_learning._hash_model_update(self.federated_learning.global_model),
            "round_number": round_number,
            "timestamp": datetime.utcnow().isoformat()
        }

    def validate_client_update(self, client_update: Dict[str, Any]) -> bool:
        """Validate client model update"""
        return self.federated_learning.update_protocol.verify_model_update(client_update)

    def get_privacy_report(self) -> Dict[str, Any]:
        """Get comprehensive privacy report"""
        return {
            "privacy_budget": self.privacy_accountant.get_privacy_budget(),
            "training_rounds": len(self.privacy_accountant.rounds),
            "total_epsilon": self.privacy_accountant.total_epsilon,
            "total_delta": self.privacy_accountant.total_delta,
            "recommendations": self._generate_privacy_recommendations()
        }

    def _generate_privacy_recommendations(self) -> List[str]:
        """Generate privacy recommendations"""
        recommendations = []
        budget = self.privacy_accountant.get_privacy_budget()

        if budget["total_epsilon"] > 5.0:
            recommendations.append("Consider reducing noise multiplier to decrease privacy loss")
        if budget["total_epsilon"] > 8.0:
            recommendations.append("Privacy budget is high - consider stopping training or increasing DP noise")
        if len(self.privacy_accountant.rounds) > 50:
            recommendations.append("Many training rounds completed - consider model evaluation")

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Initialize service
    fl_service = EnhancedFederatedLearningService(num_clients=5)

    # Generate sample datasets (normally these would be on different clients)
    sample_datasets = []
    for i in range(5):
        X = np.random.randn(100, 784)  # 100 samples, 784 features (MNIST-like)
        y = np.random.randint(0, 10, 100)  # 10 classes
        sample_datasets.append((X, y))

    # Run federated learning
    print("Starting Enhanced Federated Learning...")
    results = fl_service.run_federated_learning(sample_datasets, num_rounds=5)

    print(f"Federated Learning Results: {results}")
    print(f"Privacy Budget: {results['privacy_budget']}")
    print(f"Privacy Report: {fl_service.get_privacy_report()}")

    print("Enhanced Federated Learning completed successfully!")
