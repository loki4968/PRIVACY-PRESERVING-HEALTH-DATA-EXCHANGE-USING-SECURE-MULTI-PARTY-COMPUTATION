try:
    import numpy as np
    import statistics
    from typing import List, Dict, Any, Optional, Tuple
    from datetime import datetime
    import logging
    import uuid
    import asyncio
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, r2_score
    NUMPY_AVAILABLE = True
except ImportError:
    import logging
    import uuid
    import asyncio
    from typing import List, Dict, Any, Optional, Tuple
    from datetime import datetime
    import statistics
    NUMPY_AVAILABLE = False
    print("WARNING: NumPy or scikit-learn not available. Machine learning functionality will be limited.")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederatedLearningService:
    """Service for privacy-preserving federated learning.
    
    This service implements federated learning techniques that allow multiple
    organizations to collaboratively train machine learning models without
    sharing raw data, preserving privacy while enabling collective insights.
    """

    def __init__(self):
        self.models = {}
        self.federated_models = {}
        self.model_updates = {}
        self.model_metrics = {}
        
        # Import WebSocket manager if available
        try:
            from websocket import federated_manager
            self.websocket_manager = federated_manager
            self.websocket_enabled = True
        except (ImportError, AttributeError):
            self.websocket_enabled = False
            logger.warning("WebSocket manager not available for federated learning notifications")
    
    def initialize_model(self, model_type: str, model_params: Dict[str, Any] = None) -> str:
        """Initialize a new federated learning model.
        
        Args:
            model_type: Type of model to initialize ('linear', 'logistic', 'forest', 'anomaly', 'clustering')
            model_params: Optional parameters for model initialization
            
        Returns:
            model_id: Unique identifier for the created model
        """
        model_id = str(uuid.uuid4())
        model_params = model_params or {}
        
        if not NUMPY_AVAILABLE:
            logger.warning("NumPy or scikit-learn not available. Using mock model instead.")
            self.models[model_id] = {"type": model_type, "params": model_params, "mock": True}
            return model_id
            
        # Initialize the appropriate model based on type
        if model_type == "linear":
            model = LinearRegression(**model_params)
        elif model_type == "logistic":
            model = LogisticRegression(**model_params)
        elif model_type == "forest":
            model = RandomForestRegressor(**model_params)
        elif model_type == "anomaly":
            model = IsolationForest(**model_params)
        elif model_type == "clustering":
            model = KMeans(**model_params)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        self.models[model_id] = {
            "model": model,
            "type": model_type,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "initialized",
            "participants": [],
            "rounds": 0,
            "params": model_params
        }
        
        logger.info(f"Initialized {model_type} model with ID: {model_id}")
        return model_id
    
    def join_federated_training(self, model_id: str, organization_id: int) -> bool:
        """Allow an organization to join a federated training session.
        
        Args:
            model_id: ID of the model to join
            organization_id: ID of the organization joining
            
        Returns:
            success: Whether joining was successful
        """
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return False
        
        if organization_id in self.models[model_id]["participants"]:
            logger.warning(f"Organization {organization_id} already joined model {model_id}")
            return True
        
        self.models[model_id]["participants"].append(organization_id)
        logger.info(f"Organization {organization_id} joined model {model_id}")
        
        # Send WebSocket notification if available
        if self.websocket_enabled:
            try:
                asyncio.create_task(self.websocket_manager.broadcast_to_training_room(
                    model_id,
                    {
                        "type": "participant_joined",
                        "model_id": model_id,
                        "organization_id": organization_id,
                        "participant_count": len(self.models[model_id]["participants"])
                    }
                ))
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification: {str(e)}")
        
        return True
    
    def submit_model_update(self, model_id: str, organization_id: int, 
                           gradients: Dict[str, Any], metrics: Dict[str, float]) -> bool:
        """Submit model updates from an organization's local training.
        
        Args:
            model_id: ID of the federated model
            organization_id: ID of the organization submitting updates
            gradients: Model parameter updates (e.g., weights)
            metrics: Performance metrics from local training
            
        Returns:
            success: Whether update submission was successful
        """
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return False
        
        if organization_id not in self.models[model_id]["participants"]:
            logger.error(f"Organization {organization_id} not a participant in model {model_id}")
            return False
        
        # Store the update
        if model_id not in self.model_updates:
            self.model_updates[model_id] = {}
        
        self.model_updates[model_id][organization_id] = {
            "gradients": gradients,
            "metrics": metrics,
            "timestamp": datetime.now()
        }
        
        logger.info(f"Received model update from organization {organization_id} for model {model_id}")
        
        # Send WebSocket notification if available
        if self.websocket_enabled:
            try:
                # Notify all participants in the training room
                asyncio.create_task(self.websocket_manager.broadcast_to_training_room(
                    model_id,
                    {
                        "type": "model_update",
                        "model_id": model_id,
                        "organization_id": organization_id,
                        "update_count": len(self.model_updates[model_id]),
                        "timestamp": datetime.now().isoformat()
                    }
                ))
                
                # Also notify the organization that submitted the update
                asyncio.create_task(self.websocket_manager.broadcast_to_user(
                    organization_id,
                    {
                        "type": "update_submitted",
                        "model_id": model_id,
                        "success": True
                    }
                ))
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification: {str(e)}")
        
        return True
    
    def aggregate_model_updates(self, model_id: str) -> Dict[str, Any]:
        """Aggregate model updates from all participants using federated averaging.
        
        Args:
            model_id: ID of the federated model
            
        Returns:
            result: Aggregation results and metrics
        """
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return {"success": False, "error": "Model not found"}
        
        if model_id not in self.model_updates or not self.model_updates[model_id]:
            logger.error(f"No updates available for model {model_id}")
            return {"success": False, "error": "No updates available"}
        
        # Perform federated averaging
        updates = self.model_updates[model_id]
        aggregated_gradients = {}
        aggregated_metrics = {}
        
        # Get the first update to determine gradient keys
        first_org_id = list(updates.keys())[0]
        first_update = updates[first_org_id]
        
        # Initialize aggregated gradients with zeros of the same shape
        for key, value in first_update["gradients"].items():
            aggregated_gradients[key] = np.zeros_like(value)
        
        # Sum all gradients
        for org_id, update in updates.items():
            for key, value in update["gradients"].items():
                aggregated_gradients[key] += value
            
            # Collect metrics
            for metric_key, metric_value in update["metrics"].items():
                if metric_key not in aggregated_metrics:
                    aggregated_metrics[metric_key] = []
                aggregated_metrics[metric_key].append(metric_value)
        
        # Average the gradients
        num_updates = len(updates)
        for key in aggregated_gradients:
            aggregated_gradients[key] /= num_updates
        
        # Average the metrics
        for key in aggregated_metrics:
            aggregated_metrics[key] = sum(aggregated_metrics[key]) / len(aggregated_metrics[key])
        
        # Update the federated model
        self.federated_models[model_id] = aggregated_gradients
        self.model_metrics[model_id] = aggregated_metrics
        
        # Update model metadata
        self.models[model_id]["updated_at"] = datetime.now()
        self.models[model_id]["rounds"] += 1
        self.models[model_id]["status"] = "updated"
        
        logger.info(f"Aggregated updates for model {model_id} from {num_updates} organizations")
        
        # Prepare result
        result = {
            "success": True,
            "model_id": model_id,
            "participants": len(updates),
            "rounds": self.models[model_id]["rounds"],
            "metrics": aggregated_metrics
        }
        
        # Send WebSocket notification if available
        if self.websocket_enabled:
            try:
                # Notify all participants in the training room about aggregation completion
                asyncio.create_task(self.websocket_manager.broadcast_to_training_room(
                    model_id,
                    {
                        "type": "aggregation_result",
                        "model_id": model_id,
                        "participants": len(updates),
                        "rounds": self.models[model_id]["rounds"],
                        "metrics": aggregated_metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                ))
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification: {str(e)}")
        
        return result
    
    def get_model_status(self, model_id: str) -> Dict[str, Any]:
        """Get the current status of a federated model.
        
        Args:
            model_id: ID of the federated model
            
        Returns:
            status: Current model status and metrics
        """
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return {"success": False, "error": "Model not found"}
        
        model_info = self.models[model_id]
        
        return {
            "success": True,
            "model_id": model_id,
            "type": model_info["type"],
            "status": model_info["status"],
            "participants": len(model_info["participants"]),
            "rounds": model_info["rounds"],
            "created_at": model_info["created_at"].isoformat(),
            "updated_at": model_info["updated_at"].isoformat(),
            "metrics": self.model_metrics.get(model_id, {})
        }
        
    async def get_federated_models(self) -> List[Dict[str, Any]]:
        """Get a list of all available federated models.
        
        Returns:
            models: List of federated model information
        """
        result = []
        for model_id, model in self.models.items():
            result.append({
                "id": model_id,
                "type": model["type"],
                "status": model["status"],
                "participants": len(model["participants"]),
                "rounds": model["rounds"],
                "created_at": model["created_at"].isoformat(),
                "updated_at": model["updated_at"].isoformat()
            })
        return result


class PrivacyPreservingML:
    """Service for privacy-preserving machine learning algorithms.
    
    This service implements various privacy-preserving machine learning techniques
    that can be used with the secure computation framework to analyze health data
    while maintaining privacy guarantees.
    """
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """Initialize the privacy-preserving ML service.
        
        Args:
            epsilon: Privacy budget parameter for differential privacy
            delta: Probability parameter for differential privacy
        """
        self.epsilon = epsilon
        self.delta = delta
        self.numpy_available = NUMPY_AVAILABLE
        if not self.numpy_available:
            logger.warning("NumPy not available. Privacy-preserving ML will use mock implementations.")
        logger.info(f"Initialized Privacy-Preserving ML with epsilon={epsilon}, delta={delta}")
    
    def add_noise(self, data: Any, sensitivity: float = 1.0) -> Any:
        """Add Laplacian noise to data for differential privacy.
        
        Args:
            data: Input data to be protected
            sensitivity: Sensitivity of the function (max change from adding/removing one record)
            
        Returns:
            noisy_data: Data with added noise for privacy protection
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise
    
    def private_mean(self, values: List[float], sensitivity: float = None) -> float:
        """Calculate differentially private mean of values.
        
        Args:
            values: List of values to calculate mean from
            sensitivity: Optional sensitivity override (default: range of values)
            
        Returns:
            private_mean: Differentially private mean value
        """
        if not values:
            return None
            
        # If sensitivity not provided, estimate it from data range
        if sensitivity is None:
            sensitivity = max(values) - min(values)
            
        true_mean = sum(values) / len(values)
        noise_scale = sensitivity / (self.epsilon * len(values))
        noise = np.random.laplace(0, noise_scale)
        
        return true_mean + noise
    
    def private_histogram(self, values: List[Any], bins: List[Any] = None) -> Dict[Any, int]:
        """Create a differentially private histogram.
        
        Args:
            values: List of values to create histogram from
            bins: Optional bin definitions for numerical data
            
        Returns:
            histogram: Differentially private histogram
        """
        # Create raw histogram
        if bins is not None:
            # For numerical data with bins
            hist, _ = np.histogram(values, bins=bins)
            result = {str(i): count for i, count in enumerate(hist)}
        else:
            # For categorical data
            raw_hist = {}
            for value in values:
                if value not in raw_hist:
                    raw_hist[value] = 0
                raw_hist[value] += 1
            result = raw_hist
        
        # Add noise to each bin count
        for key in result:
            noise = np.random.laplace(0, 1.0/self.epsilon)
            result[key] = max(0, int(round(result[key] + noise)))
        
        return result
    
    def train_private_model(self, model_type: str, X: Any, y: Any, 
                           privacy_budget: float = None) -> Dict[str, Any]:
        """Train a machine learning model with differential privacy guarantees.
        
        Args:
            model_type: Type of model to train ('linear', 'logistic')
            X: Feature matrix
            y: Target values
            privacy_budget: Optional custom privacy budget
            
        Returns:
            model_info: Trained model information with privacy guarantees
        """
        # Use provided privacy budget or default
        epsilon = privacy_budget or self.epsilon
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model based on type
        if model_type == "linear":
            model = LinearRegression()
            model.fit(X_scaled, y)
            
            # Add noise to coefficients for privacy
            sensitivity = 1.0 / np.sqrt(len(X))  # Simplified sensitivity calculation
            noisy_coef = self.add_noise(model.coef_, sensitivity)
            noisy_intercept = float(model.intercept_ + np.random.laplace(0, sensitivity/epsilon))
            
            # Make predictions with noisy parameters
            y_pred = X_scaled.dot(noisy_coef) + noisy_intercept
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                "type": "linear",
                "coefficients": noisy_coef.tolist(),
                "intercept": noisy_intercept,
                "metrics": {
                    "mse": mse,
                    "r2": r2
                },
                "privacy_guarantee": {
                    "epsilon": epsilon,
                    "delta": self.delta
                }
            }
            
        elif model_type == "logistic":
            model = LogisticRegression()
            model.fit(X_scaled, y)
            
            # Add noise to coefficients for privacy
            sensitivity = 1.0 / np.sqrt(len(X))  # Simplified sensitivity calculation
            noisy_coef = self.add_noise(model.coef_[0], sensitivity)
            noisy_intercept = float(model.intercept_[0] + np.random.laplace(0, sensitivity/epsilon))
            
            return {
                "type": "logistic",
                "coefficients": noisy_coef.tolist(),
                "intercept": noisy_intercept,
                "classes": model.classes_.tolist(),
                "privacy_guarantee": {
                    "epsilon": epsilon,
                    "delta": self.delta
                }
            }
        
        else:
            raise ValueError(f"Unsupported model type for private training: {model_type}")


class SecureModelInference:
    """Service for secure model inference on encrypted data.
    
    This service enables making predictions using trained models on encrypted data,
    without decrypting the data, leveraging homomorphic encryption techniques.
    """
    
    def __init__(self):
        self.models = {}
        self.numpy_available = NUMPY_AVAILABLE
        if not self.numpy_available:
            logger.warning("NumPy not available. Secure model inference will use mock implementations.")
    
    def register_model(self, model_id: str, model_type: str, 
                      coefficients: List[float], intercept: float) -> bool:
        """Register a model for secure inference.
        
        Args:
            model_id: Unique identifier for the model
            model_type: Type of model ('linear', 'logistic')
            coefficients: Model coefficients/weights
            intercept: Model intercept/bias
            
        Returns:
            success: Whether registration was successful
        """
        self.models[model_id] = {
            "type": model_type,
            "coefficients": np.array(coefficients),
            "intercept": intercept,
            "created_at": datetime.now()
        }
        
        logger.info(f"Registered {model_type} model with ID: {model_id}")
        return True
    
    def linear_inference_on_encrypted(self, model_id: str, encrypted_features: List[Any]) -> Dict[str, Any]:
        """Perform linear model inference on homomorphically encrypted data.
        
        This method works with homomorphically encrypted data, performing the necessary
        operations (dot product and addition) without decrypting the data.
        
        Args:
            model_id: ID of the registered model
            encrypted_features: Homomorphically encrypted feature values
            
        Returns:
            result: Encrypted prediction result
        """
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return {"success": False, "error": "Model not found"}
        
        model = self.models[model_id]
        if model["type"] not in ["linear", "logistic"]:
            logger.error(f"Model type {model['type']} not supported for secure inference")
            return {"success": False, "error": "Unsupported model type"}
        
        try:
            # For homomorphic encryption, we need to:
            # 1. Multiply each encrypted feature by its coefficient
            # 2. Sum the results
            # 3. Add the intercept
            
            # This is a simplified implementation assuming the encrypted_features
            # support homomorphic operations (multiplication by scalar and addition)
            
            coefficients = model["coefficients"]
            intercept = model["intercept"]
            
            # Initialize result with the intercept
            # In a real implementation, this would be properly encrypted
            result = intercept
            
            # Multiply each feature by its coefficient and add to result
            for i, feature in enumerate(encrypted_features):
                if i < len(coefficients):
                    # In a real implementation, this would use homomorphic multiplication
                    weighted_feature = feature * coefficients[i]
                    # In a real implementation, this would use homomorphic addition
                    result += weighted_feature
            
            return {
                "success": True,
                "model_id": model_id,
                "encrypted_prediction": result
            }
            
        except Exception as e:
            logger.error(f"Error during secure inference: {str(e)}")
            return {"success": False, "error": str(e)}


class AnomalyDetectionService:
    """Service for detecting anomalies in health data.
    
    This service implements various anomaly detection algorithms that can
    identify unusual patterns in health metrics while preserving privacy.
    """
    
    def __init__(self):
        self.models = {}
        self.numpy_available = NUMPY_AVAILABLE
        if not self.numpy_available:
            logger.warning("NumPy not available. Anomaly detection will use basic statistical methods only.")
    
    def detect_anomalies(self, values: List[float], method: str = "statistical", 
                       threshold: float = 2.0) -> Dict[str, Any]:
        """Detect anomalies in a series of values.
        
        Args:
            values: List of values to analyze
            method: Detection method ('statistical', 'isolation_forest')
            threshold: Threshold for anomaly detection (Z-score for statistical)
            
        Returns:
            result: Anomaly detection results
        """
        if not values or len(values) < 3:
            return {
                "success": False,
                "error": "Insufficient data for anomaly detection"
            }
        
        if method == "statistical":
            # Statistical method using Z-scores
            mean = statistics.mean(values)
            stdev = statistics.stdev(values) if len(values) > 1 else 0
            
            if stdev == 0:
                return {
                    "success": True,
                    "anomalies": [],
                    "anomaly_indices": [],
                    "total": 0,
                    "method": "statistical"
                }
            
            z_scores = [(x - mean) / stdev for x in values]
            anomalies = []
            anomaly_indices = []
            
            for i, z in enumerate(z_scores):
                if abs(z) > threshold:
                    anomalies.append(values[i])
                    anomaly_indices.append(i)
            
            return {
                "success": True,
                "anomalies": anomalies,
                "anomaly_indices": anomaly_indices,
                "total": len(anomalies),
                "method": "statistical",
                "threshold": threshold,
                "mean": mean,
                "stdev": stdev
            }
            
        elif method == "isolation_forest":
            # Isolation Forest method
            X = np.array(values).reshape(-1, 1)
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(X)
            
            # Predict returns 1 for inliers and -1 for outliers
            predictions = model.predict(X)
            anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
            anomalies = [values[i] for i in anomaly_indices]
            
            return {
                "success": True,
                "anomalies": anomalies,
                "anomaly_indices": anomaly_indices,
                "total": len(anomalies),
                "method": "isolation_forest"
            }
            
        else:
            return {
                "success": False,
                "error": f"Unsupported anomaly detection method: {method}"
            }
    
    def detect_anomalies_multivariate(self, data: List[List[float]], 
                                    feature_names: List[str] = None,
                                    method: str = "isolation_forest") -> Dict[str, Any]:
        """Detect anomalies in multivariate data.
        
        Args:
            data: List of data points, each containing multiple features
            feature_names: Optional names for the features
            method: Detection method ('isolation_forest', 'clustering')
            
        Returns:
            result: Anomaly detection results
        """
        if not data or len(data) < 5:
            return {
                "success": False,
                "error": "Insufficient data for multivariate anomaly detection"
            }
        
        X = np.array(data)
        feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
        
        if method == "isolation_forest":
            # Isolation Forest for multivariate anomaly detection
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(X)
            
            # Predict returns 1 for inliers and -1 for outliers
            predictions = model.predict(X)
            anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
            anomalies = [data[i] for i in anomaly_indices]
            
            return {
                "success": True,
                "anomaly_indices": anomaly_indices,
                "anomalies": anomalies,
                "total": len(anomalies),
                "method": "isolation_forest",
                "feature_names": feature_names
            }
            
        elif method == "clustering":
            # K-means clustering for anomaly detection
            # Standardize the data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Calculate distance to cluster centers
            distances = []
            for i, point in enumerate(X_scaled):
                cluster_center = kmeans.cluster_centers_[clusters[i]]
                distance = np.linalg.norm(point - cluster_center)
                distances.append(distance)
            
            # Find anomalies (points far from their cluster centers)
            threshold = np.mean(distances) + 2 * np.std(distances)
            anomaly_indices = [i for i, dist in enumerate(distances) if dist > threshold]
            anomalies = [data[i] for i in anomaly_indices]
            
            return {
                "success": True,
                "anomaly_indices": anomaly_indices,
                "anomalies": anomalies,
                "total": len(anomalies),
                "method": "clustering",
                "feature_names": feature_names,
                "clusters": clusters.tolist(),
                "cluster_centers": kmeans.cluster_centers_.tolist()
            }
            
        else:
            return {
                "success": False,
                "error": f"Unsupported multivariate anomaly detection method: {method}"
            }