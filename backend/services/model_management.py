import logging
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime, timedelta
import numpy as np
import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
import joblib
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"
    FAILED = "failed"

class ModelVersion(Enum):
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"

@dataclass
class ModelMetadata:
    """Metadata for machine learning models."""
    model_id: str
    name: str
    version: str
    description: str
    algorithm: str
    task_type: str  # regression, classification, clustering, etc.
    data_type: str  # health_metrics, clinical_data, genomic_data, etc.
    features: List[str]
    target: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    tags: List[str]
    performance_metrics: Dict[str, float]
    model_size: int  # Size in bytes
    training_time: float  # Training time in seconds
    dataset_info: Dict[str, Any]

@dataclass
class ModelDeployment:
    """Information about model deployment."""
    deployment_id: str
    model_id: str
    environment: str  # development, staging, production
    deployed_at: datetime
    deployed_by: str
    endpoint_url: Optional[str]
    status: str
    performance_thresholds: Dict[str, float]
    monitoring_enabled: bool

class ModelRegistry:
    """Registry for managing ML model versions and metadata."""

    def __init__(self, registry_path: str = "model_registry/"):
        """Initialize the model registry.

        Args:
            registry_path: Path to store model registry data
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(exist_ok=True)
        self.models: Dict[str, ModelMetadata] = {}
        self.deployments: Dict[str, ModelDeployment] = {}
        self.model_versions: Dict[str, List[str]] = {}  # model_name -> list of version_ids

        # Load existing registry data
        self._load_registry()

        logger.info("Initialized Model Registry")

    def _load_registry(self):
        """Load existing registry data from disk."""
        try:
            # Load models
            models_file = self.registry_path / "models.json"
            if models_file.exists():
                with open(models_file, 'r') as f:
                    models_data = json.load(f)
                    for model_data in models_data:
                        metadata = ModelMetadata(**model_data)
                        self.models[metadata.model_id] = metadata

            # Load deployments
            deployments_file = self.registry_path / "deployments.json"
            if deployments_file.exists():
                with open(deployments_file, 'r') as f:
                    deployments_data = json.load(f)
                    for deployment_data in deployments_data:
                        deployment = ModelDeployment(**deployment_data)
                        self.deployments[deployment.deployment_id] = deployment

            # Load version tracking
            versions_file = self.registry_path / "versions.json"
            if versions_file.exists():
                with open(versions_file, 'r') as f:
                    self.model_versions = json.load(f)

        except Exception as e:
            logger.warning(f"Error loading registry data: {str(e)}")

    def _save_registry(self):
        """Save registry data to disk."""
        try:
            # Save models
            models_file = self.registry_path / "models.json"
            models_data = [asdict(metadata) for metadata in self.models.values()]
            with open(models_file, 'w') as f:
                json.dump(models_data, f, indent=2, default=str)

            # Save deployments
            deployments_file = self.registry_path / "deployments.json"
            deployments_data = [asdict(deployment) for deployment in self.deployments.values()]
            with open(deployments_file, 'w') as f:
                json.dump(deployments_data, f, indent=2, default=str)

            # Save versions
            versions_file = self.registry_path / "versions.json"
            with open(versions_file, 'w') as f:
                json.dump(self.model_versions, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving registry data: {str(e)}")

    def register_model(self,
                      name: str,
                      version: str,
                      description: str,
                      algorithm: str,
                      task_type: str,
                      data_type: str,
                      features: List[str],
                      target: str,
                      created_by: str,
                      performance_metrics: Dict[str, float],
                      model_path: str,
                      training_time: float,
                      dataset_info: Dict[str, Any],
                      tags: List[str] = None) -> str:
        """Register a new model in the registry.

        Args:
            name: Model name
            version: Model version
            description: Model description
            algorithm: ML algorithm used
            task_type: Type of ML task
            data_type: Type of data used
            features: List of feature names
            target: Target variable name
            created_by: User who created the model
            performance_metrics: Model performance metrics
            model_path: Path to the model file
            training_time: Time taken to train the model
            dataset_info: Information about the training dataset
            tags: Optional tags for the model

        Returns:
            model_id: Unique identifier for the registered model
        """
        try:
            model_id = str(uuid.uuid4())

            # Get model size
            model_size = os.path.getsize(model_path) if os.path.exists(model_path) else 0

            # Create metadata
            metadata = ModelMetadata(
                model_id=model_id,
                name=name,
                version=version,
                description=description,
                algorithm=algorithm,
                task_type=task_type,
                data_type=data_type,
                features=features,
                target=target,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=created_by,
                tags=tags or [],
                performance_metrics=performance_metrics,
                model_size=model_size,
                training_time=training_time,
                dataset_info=dataset_info
            )

            # Store metadata
            self.models[model_id] = metadata

            # Track versions
            if name not in self.model_versions:
                self.model_versions[name] = []
            self.model_versions[name].append(model_id)

            # Save registry
            self._save_registry()

            logger.info(f"Registered model {name} v{version} with ID {model_id}")

            return model_id

        except Exception as e:
            logger.error(f"Error registering model: {str(e)}")
            raise

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata by ID.

        Args:
            model_id: Model identifier

        Returns:
            model_metadata: Model metadata or None if not found
        """
        return self.models.get(model_id)

    def get_models_by_name(self, name: str) -> List[ModelMetadata]:
        """Get all versions of a model by name.

        Args:
            name: Model name

        Returns:
            models: List of model metadata for all versions
        """
        if name not in self.model_versions:
            return []

        model_ids = self.model_versions[name]
        return [self.models[model_id] for model_id in model_ids if model_id in self.models]

    def get_latest_model_version(self, name: str) -> Optional[ModelMetadata]:
        """Get the latest version of a model.

        Args:
            name: Model name

        Returns:
            latest_model: Latest version of the model or None
        """
        models = self.get_models_by_name(name)
        if not models:
            return None

        # Sort by creation time (latest first)
        models.sort(key=lambda x: x.created_at, reverse=True)
        return models[0]

    def update_model_status(self, model_id: str, status: ModelStatus, updated_by: str) -> bool:
        """Update the status of a model.

        Args:
            model_id: Model identifier
            status: New status
            updated_by: User making the update

        Returns:
            success: Whether the update was successful
        """
        if model_id not in self.models:
            return False

        # Update status and timestamp
        self.models[model_id].updated_at = datetime.now()

        # Store status in metadata (we'll add a status field)
        if not hasattr(self.models[model_id], 'status'):
            self.models[model_id].status = status.value
        else:
            self.models[model_id].status = status.value

        self._save_registry()
        logger.info(f"Updated model {model_id} status to {status.value}")

        return True

    def list_models(self,
                   algorithm: str = None,
                   task_type: str = None,
                   data_type: str = None,
                   status: str = None) -> List[ModelMetadata]:
        """List models with optional filtering.

        Args:
            algorithm: Filter by algorithm
            task_type: Filter by task type
            data_type: Filter by data type
            status: Filter by status

        Returns:
            models: List of matching models
        """
        models = list(self.models.values())

        if algorithm:
            models = [m for m in models if m.algorithm == algorithm]

        if task_type:
            models = [m for m in models if m.task_type == task_type]

        if data_type:
            models = [m for m in models if m.data_type == data_type]

        if status:
            models = [m for m in models if getattr(m, 'status', None) == status]

        return models

    def delete_model(self, model_id: str) -> bool:
        """Delete a model from the registry.

        Args:
            model_id: Model identifier

        Returns:
            success: Whether deletion was successful
        """
        try:
            if model_id not in self.models:
                return False

            # Remove from models
            model = self.models[model_id]
            del self.models[model_id]

            # Remove from version tracking
            if model.name in self.model_versions:
                if model_id in self.model_versions[model.name]:
                    self.model_versions[model.name].remove(model_id)

            # Remove model file if it exists
            model_path = Path(model.model_path) if hasattr(model, 'model_path') else None
            if model_path and model_path.exists():
                model_path.unlink()

            self._save_registry()
            logger.info(f"Deleted model {model_id}")

            return True

        except Exception as e:
            logger.error(f"Error deleting model {model_id}: {str(e)}")
            return False


class ModelDeploymentService:
    """Service for deploying and managing ML models in production."""

    def __init__(self, registry: ModelRegistry, deployment_path: str = "deployments/"):
        """Initialize the deployment service.

        Args:
            registry: Model registry instance
            deployment_path: Path to store deployment configurations
        """
        self.registry = registry
        self.deployment_path = Path(deployment_path)
        self.deployment_path.mkdir(exist_ok=True)

        logger.info("Initialized Model Deployment Service")

    def deploy_model(self,
                    model_id: str,
                    environment: str,
                    deployed_by: str,
                    endpoint_url: str = None,
                    performance_thresholds: Dict[str, float] = None,
                    monitoring_enabled: bool = True) -> Optional[str]:
        """Deploy a model to a specific environment.

        Args:
            model_id: ID of the model to deploy
            environment: Target environment (development, staging, production)
            deployed_by: User deploying the model
            endpoint_url: Optional API endpoint for the deployed model
            performance_thresholds: Performance thresholds for monitoring
            monitoring_enabled: Whether to enable performance monitoring

        Returns:
            deployment_id: Unique identifier for the deployment or None if failed
        """
        try:
            # Get model metadata
            model = self.registry.get_model(model_id)
            if not model:
                logger.error(f"Model {model_id} not found")
                return None

            # Check if model is ready for deployment
            current_status = getattr(model, 'status', None)
            if current_status != ModelStatus.TRAINED.value:
                logger.error(f"Model {model_id} is not in TRAINED status")
                return None

            deployment_id = str(uuid.uuid4())

            # Create deployment record
            deployment = ModelDeployment(
                deployment_id=deployment_id,
                model_id=model_id,
                environment=environment,
                deployed_at=datetime.now(),
                deployed_by=deployed_by,
                endpoint_url=endpoint_url,
                status="active",
                performance_thresholds=performance_thresholds or {},
                monitoring_enabled=monitoring_enabled
            )

            # Store deployment
            self.registry.deployments[deployment_id] = deployment

            # Update model status
            self.registry.update_model_status(model_id, ModelStatus.DEPLOYED, deployed_by)

            # Save deployment configuration
            deployment_config = {
                "deployment_id": deployment_id,
                "model_id": model_id,
                "model_path": getattr(model, 'model_path', ''),
                "environment": environment,
                "endpoint_url": endpoint_url,
                "performance_thresholds": performance_thresholds,
                "monitoring_config": {
                    "enabled": monitoring_enabled,
                    "metrics": ["accuracy", "precision", "recall", "latency"],
                    "alert_thresholds": {
                        "accuracy_drop": 0.05,
                        "latency_increase": 0.1
                    }
                }
            }

            config_file = self.deployment_path / f"{deployment_id}.json"
            with open(config_file, 'w') as f:
                json.dump(deployment_config, f, indent=2, default=str)

            self.registry._save_registry()

            logger.info(f"Deployed model {model_id} to {environment} as {deployment_id}")

            return deployment_id

        except Exception as e:
            logger.error(f"Error deploying model {model_id}: {str(e)}")
            return None

    def get_deployment(self, deployment_id: str) -> Optional[ModelDeployment]:
        """Get deployment information.

        Args:
            deployment_id: Deployment identifier

        Returns:
            deployment: Deployment information or None
        """
        return self.registry.deployments.get(deployment_id)

    def list_deployments(self, environment: str = None, model_id: str = None) -> List[ModelDeployment]:
        """List deployments with optional filtering.

        Args:
            environment: Filter by environment
            model_id: Filter by model ID

        Returns:
            deployments: List of matching deployments
        """
        deployments = list(self.registry.deployments.values())

        if environment:
            deployments = [d for d in deployments if d.environment == environment]

        if model_id:
            deployments = [d for d in deployments if d.model_id == model_id]

        return deployments

    def rollback_deployment(self, deployment_id: str, rolled_back_by: str) -> bool:
        """Rollback a deployment to a previous version.

        Args:
            deployment_id: Current deployment to rollback
            rolled_back_by: User performing the rollback

        Returns:
            success: Whether rollback was successful
        """
        try:
            deployment = self.get_deployment(deployment_id)
            if not deployment:
                return False

            # Get model information
            model = self.registry.get_model(deployment.model_id)
            if not model:
                return False

            # Find previous version of the same model
            previous_models = self.registry.get_models_by_name(model.name)
            previous_models = [m for m in previous_models if m.model_id != model.model_id]
            previous_models.sort(key=lambda x: x.created_at, reverse=True)

            if not previous_models:
                logger.error(f"No previous version found for model {model.name}")
                return False

            # Deploy the previous version
            previous_model = previous_models[0]
            new_deployment_id = self.deploy_model(
                model_id=previous_model.model_id,
                environment=deployment.environment,
                deployed_by=rolled_back_by,
                endpoint_url=deployment.endpoint_url,
                performance_thresholds=deployment.performance_thresholds,
                monitoring_enabled=deployment.monitoring_enabled
            )

            if new_deployment_id:
                # Mark old deployment as rolled back
                deployment.status = "rolled_back"
                self.registry._save_registry()
                logger.info(f"Rolled back deployment {deployment_id} to model {previous_model.model_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error rolling back deployment {deployment_id}: {str(e)}")
            return False

    def update_deployment_status(self, deployment_id: str, status: str, updated_by: str) -> bool:
        """Update the status of a deployment.

        Args:
            deployment_id: Deployment identifier
            status: New status
            updated_by: User making the update

        Returns:
            success: Whether update was successful
        """
        try:
            deployment = self.get_deployment(deployment_id)
            if not deployment:
                return False

            deployment.status = status
            self.registry._save_registry()

            logger.info(f"Updated deployment {deployment_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating deployment status: {str(e)}")
            return False


class ModelMonitoringService:
    """Service for monitoring deployed ML models."""

    def __init__(self, registry: ModelRegistry):
        """Initialize the monitoring service.

        Args:
            registry: Model registry instance
        """
        self.registry = registry
        self.monitoring_data: Dict[str, List[Dict[str, Any]]] = {}

        logger.info("Initialized Model Monitoring Service")

    def record_prediction(self,
                         deployment_id: str,
                         prediction: Any,
                         actual: Any = None,
                         latency: float = None,
                         features: List[float] = None) -> bool:
        """Record a model prediction for monitoring.

        Args:
            deployment_id: Deployment identifier
            prediction: Model prediction
            actual: Actual value (if available)
            latency: Prediction latency in seconds
            features: Input features used for prediction

        Returns:
            success: Whether recording was successful
        """
        try:
            deployment = self.registry.get_deployment(deployment_id)
            if not deployment:
                return False

            # Create monitoring record
            record = {
                "timestamp": datetime.now(),
                "deployment_id": deployment_id,
                "model_id": deployment.model_id,
                "prediction": prediction,
                "actual": actual,
                "latency": latency,
                "features": features
            }

            # Store record
            if deployment_id not in self.monitoring_data:
                self.monitoring_data[deployment_id] = []
            self.monitoring_data[deployment_id].append(record)

            # Keep only recent records (last 1000)
            if len(self.monitoring_data[deployment_id]) > 1000:
                self.monitoring_data[deployment_id] = self.monitoring_data[deployment_id][-1000:]

            return True

        except Exception as e:
            logger.error(f"Error recording prediction: {str(e)}")
            return False

    def get_monitoring_data(self,
                           deployment_id: str,
                           start_time: datetime = None,
                           end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get monitoring data for a deployment.

        Args:
            deployment_id: Deployment identifier
            start_time: Start time for data filter
            end_time: End time for data filter

        Returns:
            monitoring_data: List of monitoring records
        """
        try:
            if deployment_id not in self.monitoring_data:
                return []

            data = self.monitoring_data[deployment_id]

            # Filter by time if specified
            if start_time:
                data = [record for record in data if record["timestamp"] >= start_time]
            if end_time:
                data = [record for record in data if record["timestamp"] <= end_time]

            return data

        except Exception as e:
            logger.error(f"Error getting monitoring data: {str(e)}")
            return []

    def calculate_performance_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """Calculate performance metrics from monitoring data.

        Args:
            deployment_id: Deployment identifier

        Returns:
            metrics: Performance metrics
        """
        try:
            data = self.get_monitoring_data(deployment_id)

            if not data:
                return {"error": "No monitoring data available"}

            # Calculate basic metrics
            total_predictions = len(data)
            avg_latency = np.mean([r["latency"] for r in data if r["latency"] is not None])

            # Calculate accuracy if actual values are available
            accuracy = None
            if any(r["actual"] is not None for r in data):
                correct_predictions = sum(1 for r in data if r["actual"] is not None and r["prediction"] == r["actual"])
                accuracy = correct_predictions / sum(1 for r in data if r["actual"] is not None)

            # Calculate prediction distribution
            predictions = [r["prediction"] for r in data]
            unique_predictions = set(predictions)
            prediction_distribution = {pred: predictions.count(pred) / total_predictions for pred in unique_predictions}

            metrics = {
                "total_predictions": total_predictions,
                "average_latency": avg_latency,
                "accuracy": accuracy,
                "prediction_distribution": prediction_distribution,
                "monitoring_period": {
                    "start": min(r["timestamp"] for r in data),
                    "end": max(r["timestamp"] for r in data)
                }
            }

            return metrics

        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {"error": str(e)}

    def check_performance_alerts(self, deployment_id: str) -> Dict[str, Any]:
        """Check for performance alerts based on thresholds.

        Args:
            deployment_id: Deployment identifier

        Returns:
            alerts: Alert information
        """
        try:
            deployment = self.registry.get_deployment(deployment_id)
            if not deployment:
                return {"error": "Deployment not found"}

            metrics = self.calculate_performance_metrics(deployment_id)
            alerts = []

            # Check accuracy threshold
            if metrics.get("accuracy") is not None:
                accuracy_threshold = deployment.performance_thresholds.get("accuracy", 0.8)
                if metrics["accuracy"] < accuracy_threshold:
                    alerts.append({
                        "type": "accuracy_degraded",
                    "message": f"Model accuracy {metrics['accuracy']:.3f} below threshold {accuracy_threshold}",
                        "severity": "high"
                    })

            # Check latency threshold
            if metrics.get("average_latency") is not None:
                latency_threshold = deployment.performance_thresholds.get("latency", 1.0)
                if metrics["average_latency"] > latency_threshold:
                    alerts.append({
                        "type": "high_latency",
                        "message": f"Average latency {metrics['average_latency']".3f"}s exceeds threshold {latency_threshold}s",
                        "severity": "medium"
                    })

            return {
                "deployment_id": deployment_id,
                "alerts": alerts,
                "alert_count": len(alerts)
            }

        except Exception as e:
            logger.error(f"Error checking performance alerts: {str(e)}")
            return {"error": str(e)}


# Global instances
model_registry = ModelRegistry()
deployment_service = ModelDeploymentService(model_registry)
monitoring_service = ModelMonitoringService(model_registry)
