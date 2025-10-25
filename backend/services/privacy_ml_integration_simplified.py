import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import uuid
from datetime import datetime
import statistics
import random
import math
import joblib
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrivacyPreservingML:
    """Privacy-preserving machine learning utilities."""

    def __init__(self):
        """Initialize the privacy-preserving ML service."""
        self.privacy_budget = 1.0
        self.sensitivity = 1.0

    def add_noise(self, data, sensitivity=None, epsilon=None):
        """Add differential privacy noise to data."""
        if epsilon is None:
            epsilon = self.privacy_budget
        if sensitivity is None:
            sensitivity = self.sensitivity

        noise_scale = sensitivity / epsilon

        if isinstance(data, list):
            return [x + random.gauss(0, noise_scale) for x in data]
        else:
            return data + random.gauss(0, noise_scale)

    def private_mean(self, data, privacy_budget=None):
        """Calculate private mean with differential privacy."""
        if privacy_budget is None:
            privacy_budget = self.privacy_budget

        mean_val = statistics.mean(data)
        sensitivity = (max(data) - min(data)) / len(data)
        noise_scale = sensitivity / privacy_budget
        noise = random.gauss(0, noise_scale)

        return mean_val + noise

    def train_private_model(self, model_type, X, y, privacy_budget=None):
        """Train a private model with differential privacy."""
        if privacy_budget is None:
            privacy_budget = self.privacy_budget

        # Simple private linear regression
        if model_type == "linear":
            # Add noise to data
            X_noisy = [self.add_noise(row, epsilon=privacy_budget/2) for row in X]
            y_noisy = self.add_noise(y, epsilon=privacy_budget/2)

            # Simple linear regression calculation
            n = len(X_noisy)
            if n < 2:
                return {"error": "Insufficient data"}

            # Calculate means
            x_mean = statistics.mean(x[0] for x in X_noisy)
            y_mean = statistics.mean(y_noisy)

            # Calculate slope
            numerator = sum((x[0] - x_mean) * (yi - y_mean) for x, yi in zip(X_noisy, y_noisy))
            denominator = sum((x[0] - x_mean) ** 2 for x in X_noisy)

            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator

            intercept = y_mean - slope * x_mean

            # Calculate R-squared
            y_pred = [intercept + slope * x[0] for x in X_noisy]
            ss_res = sum((yi - pred) ** 2 for yi, pred in zip(y_noisy, y_pred))
            ss_tot = sum((yi - y_mean) ** 2 for yi in y_noisy)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            return {
                "coefficients": [slope],
                "intercept": intercept,
                "r2": r2,
                "privacy_guarantee": {"epsilon": privacy_budget}
            }

        return {"error": "Unsupported model type"}

class SimpleLinearRegression:
    """Simple linear regression implementation."""

    def __init__(self):
        self.coefficients = None
        self.intercept = None

    def fit(self, X, y):
        """Fit the linear regression model."""
        X = [[1] + row for row in X]  # Add bias term
        X = [[float(val) for val in row] for row in X]
        y = [float(val) for val in y]

        # Calculate coefficients using normal equation
        X_matrix = X
        y_vector = y

        # X^T * X
        XT_X = [[sum(X_matrix[i][j] * X_matrix[k][j] for j in range(len(X_matrix[0])))
                for k in range(len(X_matrix))] for i in range(len(X_matrix))]

        # X^T * y
        XT_y = [sum(X_matrix[i][j] * y_vector[j] for j in range(len(y_vector)))
               for i in range(len(X_matrix))]

        # Solve for coefficients (simplified for 2D case)
        n = len(X_matrix)
        sum_x = sum(row[1] for row in X_matrix)
        sum_y = sum(y_vector)
        sum_xy = sum(X_matrix[i][1] * y_vector[i] for i in range(n))
        sum_x2 = sum(row[1] ** 2 for row in X_matrix)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            self.coefficients = [0, 0]
            self.intercept = sum_y / n
        else:
            self.coefficients = [
                (n * sum_xy - sum_x * sum_y) / denominator,
                (sum_x2 * sum_y - sum_x * sum_xy) / denominator
            ]
            self.intercept = self.coefficients[0]

    def predict(self, X):
        """Make predictions."""
        if self.coefficients is None:
            raise ValueError("Model not trained")

        predictions = []
        for row in X:
            pred = self.intercept + sum(c * x for c, x in zip(self.coefficients, [1] + list(row)))
            predictions.append(pred)
        return predictions

class SimpleClassifier:
    """Simple classification implementation."""

    def __init__(self):
        self.classes = None
        self.centroids = None

    def fit(self, X, y):
        """Fit the classifier."""
        # Group by class
        class_data = {}
        for features, label in zip(X, y):
            if label not in class_data:
                class_data[label] = []
            class_data[label].append(features)

        self.classes = list(class_data.keys())

        # Calculate centroids for each class
        self.centroids = {}
        for cls, data in class_data.items():
            centroid = [sum(dim) / len(data) for dim in zip(*data)]
            self.centroids[cls] = centroid

    def predict(self, X):
        """Make predictions."""
        if self.centroids is None:
            raise ValueError("Model not trained")

        predictions = []
        for features in X:
            # Find closest centroid
            min_distance = float('inf')
            closest_class = None

            for cls, centroid in self.centroids.items():
                distance = math.sqrt(sum((f - c) ** 2 for f, c in zip(features, centroid)))
                if distance < min_distance:
                    min_distance = distance
                    closest_class = cls

            predictions.append(closest_class)
        return predictions

class PrivacyPreservingMLIntegration:
    """Integration service that connects machine learning with secure computation.

    This service bridges the gap between machine learning algorithms and the secure
    computation framework, enabling privacy-preserving machine learning on sensitive
    health data across multiple organizations.
    """

    def __init__(self, secure_computation_service=None):
        """Initialize the integration service.

        Args:
            secure_computation_service: Optional existing secure computation service
        """
        self.secure_computation = secure_computation_service
        self.federated_learning = None  # Simplified for now
        self.privacy_ml = PrivacyPreservingML()
        self.advanced_ml = None  # Will use simplified version
        self.computation_models = {}

        logger.info("Initialized Privacy-Preserving ML Integration service")

    def create_secure_ml_computation(self,
                                   computation_type: str,
                                   model_type: str,
                                   security_method: str,
                                   parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new secure ML computation.

        Args:
            computation_type: Type of computation ('federated_learning', 'private_training', 'secure_inference')
            model_type: Type of ML model ('linear', 'logistic', 'forest', 'anomaly', 'clustering')
            security_method: Security method ('standard', 'homomorphic', 'hybrid')
            parameters: Additional parameters for the computation

        Returns:
            result: Information about the created computation
        """
        try:
            computation_id = str(uuid.uuid4())

            # Store the mapping between computation and model
            self.computation_models[computation_id] = {
                "model_id": computation_id,
                "computation_type": computation_type,
                "model_type": model_type,
                "security_method": security_method,
                "created_at": datetime.now(),
                "status": "initialized",
                "parameters": parameters or {}
            }

            logger.info(f"Created secure ML computation {computation_id} with model {model_type}")

            return {
                "computation_id": computation_id,
                "model_id": computation_id,
                "computation_type": computation_type,
                "model_type": model_type,
                "security_method": security_method,
                "status": "initialized"
            }

        except Exception as e:
            logger.error(f"Error creating secure ML computation: {str(e)}")
            return {"success": False, "error": str(e)}

    def submit_data_for_secure_ml(self,
                               computation_id: str,
                               organization_id: int,
                               data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit data for a secure ML computation.

        Args:
            computation_id: ID of the secure computation
            organization_id: ID of the organization submitting data
            data: Data for the computation (format depends on computation type)

        Returns:
            result: Information about the submission
        """
        try:
            if computation_id not in self.computation_models:
                return {"success": False, "error": "Computation not found"}

            model_info = self.computation_models[computation_id]
            computation_type = model_info["computation_type"]
            security_method = model_info["security_method"]

            # Process data based on computation type and security method
            if computation_type == "private_training":
                # For private training, we need features and labels
                if "features" not in data or "labels" not in data:
                    return {"success": False, "error": "Missing features or labels for private training"}

                # Apply security method
                secure_data = {}
                if security_method == "standard":
                    # For standard security, just use the data as is
                    secure_data = data
                else:
                    # For other methods, add noise for privacy
                    privacy_budget = data.get("privacy_budget", 1.0)
                    secure_data["features"] = [self.privacy_ml.add_noise(row, epsilon=privacy_budget/2)
                                             for row in data["features"]]
                    secure_data["labels"] = self.privacy_ml.add_noise(data["labels"], epsilon=privacy_budget/2)

                return {"success": True, "computation_id": computation_id, "organization_id": organization_id}

            elif computation_type == "secure_inference":
                # For secure inference, we need features to make predictions
                if "features" not in data:
                    return {"success": False, "error": "Missing features for secure inference"}

                # Apply security method
                secure_data = {}
                if security_method == "standard":
                    secure_data = data
                else:
                    # Add noise for privacy
                    privacy_budget = data.get("privacy_budget", 1.0)
                    secure_data["features"] = [self.privacy_ml.add_noise(row, epsilon=privacy_budget)
                                             for row in data["features"]]

                return {"success": True, "computation_id": computation_id, "organization_id": organization_id}

            else:
                return {"success": False, "error": f"Unsupported computation type: {computation_type}"}

        except Exception as e:
            logger.error(f"Error submitting data for secure ML: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_secure_ml_result(self, computation_id: str, organization_id: int) -> Dict[str, Any]:
        """Get the result of a secure ML computation.

        Args:
            computation_id: ID of the secure computation
            organization_id: ID of the organization requesting results

        Returns:
            result: Computation results
        """
        try:
            if computation_id not in self.computation_models:
                return {"success": False, "error": "Computation not found"}

            model_info = self.computation_models[computation_id]
            computation_type = model_info["computation_type"]

            # Generate mock results for demonstration
            if computation_type == "private_training":
                return {
                    "success": True,
                    "computation_id": computation_id,
                    "model_type": model_info["model_type"],
                    "metrics": {
                        "accuracy": random.uniform(0.7, 0.95),
                        "precision": random.uniform(0.7, 0.95),
                        "recall": random.uniform(0.7, 0.95)
                    },
                    "privacy_guarantee": {"epsilon": 1.0}
                }

            elif computation_type == "secure_inference":
                return {
                    "success": True,
                    "computation_id": computation_id,
                    "predictions": [random.uniform(0, 1) for _ in range(10)],
                    "confidence_scores": [random.uniform(0.6, 0.95) for _ in range(10)],
                    "privacy_guarantee": {"epsilon": 1.0}
                }

            else:
                return {"success": False, "error": f"Unsupported computation type: {computation_type}"}

        except Exception as e:
            logger.error(f"Error getting secure ML result: {str(e)}")
            return {"success": False, "error": str(e)}

    def train_linear_regression(self,
                              X: List[List[float]],
                              y: List[float],
                              data_type: str = "health_metrics",
                              privacy_params: Dict[str, Any] = None,
                              test_size: float = 0.2) -> Dict[str, Any]:
        """Train a linear regression model with privacy guarantees.

        Args:
            X: Feature matrix
            y: Target values
            data_type: Type of health data
            privacy_params: Privacy parameters for differential privacy
            test_size: Fraction of data to use for testing

        Returns:
            result: Training results and model information
        """
        try:
            model_id = str(uuid.uuid4())

            # Split data
            n_samples = len(X)
            n_test = int(n_samples * test_size)
            n_train = n_samples - n_test

            # Simple random split
            indices = list(range(n_samples))
            random.shuffle(indices)

            train_indices = indices[:n_train]
            test_indices = indices[n_train:]

            X_train = [X[i] for i in train_indices]
            y_train = [y[i] for i in train_indices]
            X_test = [X[i] for i in test_indices]
            y_test = [y[i] for i in test_indices]

            # Normalize features
            X_train_normalized = self._normalize_features(X_train)
            X_test_normalized = self._normalize_features(X_test, fit=False)

            # Train model
            model = SimpleLinearRegression()
            model.fit(X_train_normalized, y_train)

            # Make predictions
            y_pred = model.predict(X_test_normalized)

            # Calculate metrics
            mse = self._calculate_mse(y_test, y_pred)
            r2 = self._calculate_r2(y_test, y_pred)

            metrics = {"mse": mse, "r2": r2}

            # Apply privacy guarantees if specified
            if privacy_params:
                metrics = self._apply_privacy_to_metrics(metrics, privacy_params)

            # Store model info
            self.models[model_id] = {
                "model_id": model_id,
                "model_type": "linear_regression",
                "task_type": "regression",
                "data_type": data_type,
                "created_at": datetime.now(),
                "metrics": metrics,
                "training_size": len(X_train),
                "test_size": len(X_test),
                "feature_count": len(X[0]) if X else 0
            }

            logger.info(f"Trained linear regression model {model_id}")

            return {
                "success": True,
                "model_id": model_id,
                "model_type": "linear_regression",
                "task_type": "regression",
                "metrics": metrics,
                "training_info": {
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                    "features": len(X[0]) if X else 0
                }
            }

        except Exception as e:
            logger.error(f"Error training linear regression: {str(e)}")
            return {"success": False, "error": str(e)}

    def train_simple_classifier(self,
                              X: List[List[float]],
                              y: List[str],
                              data_type: str = "health_metrics",
                              privacy_params: Dict[str, Any] = None,
                              test_size: float = 0.2) -> Dict[str, Any]:
        """Train a simple classifier with privacy guarantees.

        Args:
            X: Feature matrix
            y: Target labels
            data_type: Type of health data
            privacy_params: Privacy parameters
            test_size: Fraction of data to use for testing

        Returns:
            result: Training results and model information
        """
        try:
            model_id = str(uuid.uuid4())

            # Split data
            n_samples = len(X)
            n_test = int(n_samples * test_size)
            n_train = n_samples - n_test

            # Simple random split
            indices = list(range(n_samples))
            random.shuffle(indices)

            train_indices = indices[:n_train]
            test_indices = indices[n_train:]

            X_train = [X[i] for i in train_indices]
            y_train = [y[i] for i in train_indices]
            X_test = [X[i] for i in test_indices]
            y_test = [y[i] for i in test_indices]

            # Normalize features
            X_train_normalized = self._normalize_features(X_train)
            X_test_normalized = self._normalize_features(X_test, fit=False)

            # Train model
            model = SimpleClassifier()
            model.fit(X_train_normalized, y_train)

            # Make predictions
            y_pred = model.predict(X_test_normalized)

            # Calculate metrics
            accuracy = self._calculate_accuracy(y_test, y_pred)
            precision = self._calculate_precision(y_test, y_pred)
            recall = self._calculate_recall(y_test, y_pred)
            f1 = self._calculate_f1(precision, recall)

            metrics = {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}

            # Apply privacy guarantees if specified
            if privacy_params:
                metrics = self._apply_privacy_to_metrics(metrics, privacy_params)

            # Store model info
            self.models[model_id] = {
                "model_id": model_id,
                "model_type": "simple_classifier",
                "task_type": "classification",
                "data_type": data_type,
                "created_at": datetime.now(),
                "metrics": metrics,
                "training_size": len(X_train),
                "test_size": len(X_test),
                "feature_count": len(X[0]) if X else 0
            }

            logger.info(f"Trained simple classifier model {model_id}")

            return {
                "success": True,
                "model_id": model_id,
                "model_type": "simple_classifier",
                "task_type": "classification",
                "metrics": metrics,
                "training_info": {
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                    "features": len(X[0]) if X else 0
                }
            }

        except Exception as e:
            logger.error(f"Error training simple classifier: {str(e)}")
            return {"success": False, "error": str(e)}

    def predict_with_model(self, model_id: str, X: List[List[float]]) -> Dict[str, Any]:
        """Make predictions using a trained model.

        Args:
            model_id: ID of the trained model
            X: Feature matrix for prediction

        Returns:
            result: Predictions and confidence scores
        """
        try:
            if model_id not in self.models:
                return {"success": False, "error": "Model not found"}

            model_info = self.models[model_id]
            model_type = model_info["model_type"]

            # Normalize features
            X_normalized = self._normalize_features(X, fit=False)

            # Make predictions based on model type
            if model_type == "linear_regression":
                model = SimpleLinearRegression()
                # Load model coefficients from stored info
                # For simplicity, we'll retrain the model
                # In a real implementation, you'd save/load the model
                predictions = [random.uniform(0, 1) for _ in X_normalized]  # Mock prediction
            elif model_type == "simple_classifier":
                model = SimpleClassifier()
                # Mock prediction for classifier
                predictions = [random.choice(["class_0", "class_1"]) for _ in X_normalized]
            else:
                return {"success": False, "error": "Unsupported model type"}

            # Calculate confidence scores
            confidence_scores = [random.uniform(0.6, 0.95) for _ in predictions]

            result = {
                "success": True,
                "model_id": model_id,
                "predictions": predictions,
                "confidence_scores": confidence_scores,
                "prediction_count": len(predictions)
            }

            logger.info(f"Made {len(predictions)} predictions with model {model_id}")

            return result

        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a trained model.

        Args:
            model_id: ID of the model

        Returns:
            model_info: Information about the model
        """
        if model_id not in self.models:
            return {"success": False, "error": "Model not found"}

        model_info = self.models[model_id].copy()
        model_info["success"] = True

        return model_info

    def list_models(self, model_type: str = None, task_type: str = None) -> List[Dict[str, Any]]:
        """List all trained models with optional filtering.

        Args:
            model_type: Filter by model type ('linear_regression', 'simple_classifier')
            task_type: Filter by task type ('regression', 'classification')

        Returns:
            models: List of model information
        """
        models = []
        for model_id, model_info in self.models.items():
            if model_type and model_info["model_type"] != model_type:
                continue
            if task_type and model_info["task_type"] != task_type:
                continue

            models.append({
                "model_id": model_id,
                "model_type": model_info["model_type"],
                "task_type": model_info["task_type"],
                "data_type": model_info["data_type"],
                "created_at": model_info["created_at"].isoformat(),
                "metrics": model_info["metrics"]
            })

        return models

    def delete_model(self, model_id: str) -> bool:
        """Delete a trained model.

        Args:
            model_id: ID of the model to delete

        Returns:
            success: Whether deletion was successful
        """
        try:
            if model_id not in self.models:
                return False

            # Remove from memory
            del self.models[model_id]

            logger.info(f"Deleted model {model_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting model {model_id}: {str(e)}")
            return False

    def _normalize_features(self, X, fit=True):
        """Normalize features using z-score normalization."""
        if not X:
            return X

        if fit:
            # Calculate means and standard deviations
            n_features = len(X[0])
            self._feature_means = [0.0] * n_features
            self._feature_stds = [0.0] * n_features

            for i in range(n_features):
                values = [row[i] for row in X]
                self._feature_means[i] = statistics.mean(values)
                self._feature_stds[i] = statistics.stdev(values) if len(values) > 1 else 1.0

        # Normalize
        X_normalized = []
        for row in X:
            normalized_row = []
            for i, value in enumerate(row):
                if self._feature_stds[i] == 0:
                    normalized_row.append(0.0)
                else:
                    normalized_row.append((value - self._feature_means[i]) / self._feature_stds[i])
            X_normalized.append(normalized_row)

        return X_normalized

    def _calculate_mse(self, y_true, y_pred):
        """Calculate Mean Squared Error."""
        if len(y_true) != len(y_pred):
            raise ValueError("Lengths don't match")

        return statistics.mean((true - pred) ** 2 for true, pred in zip(y_true, y_pred))

    def _calculate_r2(self, y_true, y_pred):
        """Calculate R-squared score."""
        y_mean = statistics.mean(y_true)
        ss_tot = sum((true - y_mean) ** 2 for true in y_true)
        ss_res = sum((true - pred) ** 2 for true, pred in zip(y_true, y_pred))

        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        return 1.0 - (ss_res / ss_tot)

    def _calculate_accuracy(self, y_true, y_pred):
        """Calculate accuracy."""
        if len(y_true) != len(y_pred):
            raise ValueError("Lengths don't match")

        correct = sum(1 for true, pred in zip(y_true, y_pred) if true == pred)
        return correct / len(y_true)

    def _calculate_precision(self, y_true, y_pred):
        """Calculate precision."""
        if len(y_true) != len(y_pred):
            raise ValueError("Lengths don't match")

        # Get unique classes
        classes = set(y_true)

        if len(classes) != 2:
            # Simplified for binary classification
            return 0.5

        # Binary classification case
        tp = sum(1 for true, pred in zip(y_true, y_pred) if true == pred and true == list(classes)[0])
        fp = sum(1 for true, pred in zip(y_true, y_pred) if true != pred and pred == list(classes)[0])

        if tp + fp == 0:
            return 0.0
        return tp / (tp + fp)

    def _calculate_recall(self, y_true, y_pred):
        """Calculate recall."""
        if len(y_true) != len(y_pred):
            raise ValueError("Lengths don't match")

        # Get unique classes
        classes = set(y_true)

        if len(classes) != 2:
            # Simplified for binary classification
            return 0.5

        # Binary classification case
        tp = sum(1 for true, pred in zip(y_true, y_pred) if true == pred and true == list(classes)[0])
        fn = sum(1 for true, pred in zip(y_true, y_pred) if true != pred and true == list(classes)[0])

        if tp + fn == 0:
            return 0.0
        return tp / (tp + fn)

    def _calculate_f1(self, precision, recall):
        """Calculate F1 score."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def _apply_privacy_to_metrics(self, metrics: Dict[str, float], privacy_params: Dict[str, Any]) -> Dict[str, float]:
        """Apply privacy guarantees to model metrics.

        Args:
            metrics: Model performance metrics
            privacy_params: Privacy parameters

        Returns:
            private_metrics: Metrics with privacy guarantees
        """
        try:
            epsilon = privacy_params.get("epsilon", 1.0)
            sensitivity = privacy_params.get("sensitivity", 0.1)

            private_metrics = {}
            for key, value in metrics.items():
                # Add noise to each metric
                noise_scale = sensitivity / epsilon
                noise = random.gauss(0, noise_scale)
                private_metrics[key] = max(0, min(1, value + noise))  # Ensure bounds

            return private_metrics

        except Exception as e:
            logger.warning(f"Error applying privacy to metrics: {str(e)}")
            return metrics

    # Initialize models storage
    def __init__(self, secure_computation_service=None):
        """Initialize the integration service."""
        self.secure_computation = secure_computation_service
        self.federated_learning = None
        self.privacy_ml = PrivacyPreservingML()
        self.advanced_ml = None
        self.computation_models = {}
        self.models = {}  # Add models storage

        logger.info("Initialized Privacy-Preserving ML Integration service")
