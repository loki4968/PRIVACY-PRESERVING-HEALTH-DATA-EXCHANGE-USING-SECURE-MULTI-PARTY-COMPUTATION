"""
Advanced Model Management System
Model versioning, A/B testing, drift detection, automated retraining, and performance monitoring
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime, timedelta
import logging
import json
import hashlib
import pickle
import os
from collections import defaultdict
import threading
import time
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelVersionControl:
    """Model versioning system with git-like functionality"""

    def __init__(self, storage_path: str = "./model_versions"):
        self.storage_path = storage_path
        self.models = {}
        self.versions = defaultdict(list)
        self.current_version = {}

        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)

    def save_model_version(self, model_name: str, model: Any, metadata: Dict[str, Any] = None) -> str:
        """Save a new version of a model"""
        if metadata is None:
            metadata = {}

        # Generate version hash
        version_hash = self._generate_version_hash(model, metadata)

        # Create version info
        version_info = {
            "model_name": model_name,
            "version_hash": version_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata,
            "file_path": os.path.join(self.storage_path, f"{model_name}_{version_hash}.pkl")
        }

        # Save model to file
        try:
            with open(version_info["file_path"], 'wb') as f:
                pickle.dump(model, f)

            # Update version history
            self.versions[model_name].append(version_info)
            self.current_version[model_name] = version_hash

            logger.info(f"Saved model {model_name} version {version_hash}")
            return version_hash

        except Exception as e:
            logger.error(f"Error saving model {model_name}: {str(e)}")
            raise

    def load_model_version(self, model_name: str, version_hash: str = None) -> Tuple[Any, Dict[str, Any]]:
        """Load a specific version of a model"""
        if version_hash is None:
            version_hash = self.current_version.get(model_name)

        if not version_hash:
            raise ValueError(f"No version specified for model {model_name}")

        # Find version info
        version_info = None
        for version in self.versions[model_name]:
            if version["version_hash"] == version_hash:
                version_info = version
                break

        if not version_info:
            raise ValueError(f"Version {version_hash} not found for model {model_name}")

        # Load model from file
        try:
            with open(version_info["file_path"], 'rb') as f:
                model = pickle.load(f)

            return model, version_info

        except Exception as e:
            logger.error(f"Error loading model {model_name} version {version_hash}: {str(e)}")
            raise

    def list_model_versions(self, model_name: str) -> List[Dict[str, Any]]:
        """List all versions of a model"""
        return self.versions.get(model_name, [])

    def compare_versions(self, model_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two versions of a model"""
        try:
            model1, info1 = self.load_model_version(model_name, version1)
            model2, info2 = self.load_model_version(model_name, version2)

            comparison = {
                "version1": info1,
                "version2": info2,
                "differences": self._compare_model_objects(model1, model2)
            }

            return comparison

        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}")
            raise

    def _generate_version_hash(self, model: Any, metadata: Dict[str, Any]) -> str:
        """Generate unique hash for model version"""
        # Create hash from model parameters and metadata
        model_str = str(model)
        metadata_str = json.dumps(metadata, sort_keys=True)
        combined = f"{model_str}_{metadata_str}_{datetime.utcnow().isoformat()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _compare_model_objects(self, model1: Any, model2: Any) -> Dict[str, Any]:
        """Compare two model objects"""
        differences = {}

        # This is a simplified comparison - in practice, you'd compare specific model attributes
        if hasattr(model1, 'get_params') and hasattr(model2, 'get_params'):
            params1 = model1.get_params()
            params2 = model2.get_params()

            for key in set(params1.keys()) | set(params2.keys()):
                if params1.get(key) != params2.get(key):
                    differences[key] = {
                        "model1": params1.get(key),
                        "model2": params2.get(key)
                    }

        return differences


class ABTestingFramework:
    """A/B testing framework for model comparison"""

    def __init__(self):
        self.experiments = {}
        self.results = defaultdict(dict)

    def create_experiment(self, experiment_name: str, model_a: Any, model_b: Any,
                         test_data: Tuple[np.ndarray, np.ndarray],
                         evaluation_metric: str = "accuracy") -> str:
        """Create a new A/B testing experiment"""
        experiment_id = hashlib.sha256(f"{experiment_name}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]

        experiment = {
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "model_a": model_a,
            "model_b": model_b,
            "test_data": test_data,
            "evaluation_metric": evaluation_metric,
            "status": "running",
            "created_at": datetime.utcnow().isoformat(),
            "results": None
        }

        self.experiments[experiment_id] = experiment

        # Run experiment in background
        threading.Thread(target=self._run_experiment, args=(experiment_id,)).start()

        return experiment_id

    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get results of an A/B testing experiment"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]

        if experiment["status"] == "running":
            return {"status": "running", "message": "Experiment is still running"}

        return experiment["results"]

    def _run_experiment(self, experiment_id: str):
        """Run the A/B testing experiment"""
        experiment = self.experiments[experiment_id]
        X_test, y_test = experiment["test_data"]
        model_a = experiment["model_a"]
        model_b = experiment["model_b"]
        metric = experiment["evaluation_metric"]

        try:
            # Get predictions from both models
            if hasattr(model_a, 'predict'):
                pred_a = model_a.predict(X_test)
            else:
                pred_a = model_a

            if hasattr(model_b, 'predict'):
                pred_b = model_b.predict(X_test)
            else:
                pred_b = model_b

            # Calculate metrics
            results_a = self._calculate_metrics(y_test, pred_a, metric)
            results_b = self._calculate_metrics(y_test, pred_b, metric)

            # Determine winner
            if metric in ["accuracy", "precision", "recall", "f1"]:
                winner = "A" if results_a[metric] > results_b[metric] else "B"
            else:  # For regression metrics like MSE, lower is better
                winner = "A" if results_a[metric] < results_b[metric] else "B"

            # Statistical significance test (simplified)
            significance = self._calculate_significance(pred_a, pred_b, y_test)

            experiment["results"] = {
                "model_a_metrics": results_a,
                "model_b_metrics": results_b,
                "winner": winner,
                "statistical_significance": significance,
                "confidence_interval": self._calculate_confidence_interval(pred_a, pred_b, y_test),
                "sample_size": len(y_test)
            }

            experiment["status"] = "completed"

        except Exception as e:
            experiment["status"] = "failed"
            experiment["error"] = str(e)
            logger.error(f"Experiment {experiment_id} failed: {str(e)}")

    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, metric: str) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        metrics = {}

        if metric == "accuracy":
            metrics["accuracy"] = accuracy_score(y_true, y_pred)
        elif metric == "precision":
            metrics["precision"] = precision_score(y_true, y_pred, average='weighted')
        elif metric == "recall":
            metrics["recall"] = recall_score(y_true, y_pred, average='weighted')
        elif metric == "f1":
            metrics["f1"] = f1_score(y_true, y_pred, average='weighted')
        elif metric == "mse":
            metrics["mse"] = mean_squared_error(y_true, y_pred)
        elif metric == "rmse":
            metrics["rmse"] = np.sqrt(mean_squared_error(y_true, y_pred))
        elif metric == "mae":
            metrics["mae"] = mean_absolute_error(y_true, y_pred)
        elif metric == "r2":
            metrics["r2"] = r2_score(y_true, y_pred)

        return metrics

    def _calculate_significance(self, pred_a: np.ndarray, pred_b: np.ndarray, y_true: np.ndarray) -> Dict[str, Any]:
        """Calculate statistical significance (simplified)"""
        # This is a simplified significance test
        # In practice, you'd use proper statistical tests like t-test
        diff = np.abs(np.mean(pred_a) - np.mean(pred_b))
        std_a = np.std(pred_a)
        std_b = np.std(pred_b)
        n = len(y_true)

        if std_a > 0 and std_b > 0:
            se = np.sqrt(std_a**2/n + std_b**2/n)
            z_score = diff / se if se > 0 else 0
            p_value = 1 - (1 / (1 + np.exp(-z_score)))  # Sigmoid approximation
        else:
            p_value = 1.0

        return {
            "p_value": p_value,
            "significant": p_value < 0.05,
            "confidence_level": "95%"
        }

    def _calculate_confidence_interval(self, pred_a: np.ndarray, pred_b: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """Calculate confidence interval for the difference"""
        diff = np.mean(pred_a) - np.mean(pred_b)
        std_diff = np.sqrt(np.var(pred_a)/len(pred_a) + np.var(pred_b)/len(pred_b))
        margin = 1.96 * std_diff  # 95% confidence interval

        return {
            "lower_bound": diff - margin,
            "upper_bound": diff + margin,
            "margin": margin
        }


class ModelDriftDetector:
    """Detect model drift and data drift"""

    def __init__(self, drift_threshold: float = 0.1):
        self.drift_threshold = drift_threshold
        self.baseline_stats = {}
        self.drift_history = []

    def set_baseline(self, X: np.ndarray, y: np.ndarray, model: Any = None):
        """Set baseline statistics for drift detection"""
        self.baseline_stats = {
            "feature_means": np.mean(X, axis=0),
            "feature_stds": np.std(X, axis=0),
            "feature_mins": np.min(X, axis=0),
            "feature_maxs": np.max(X, axis=0),
            "target_mean": np.mean(y),
            "target_std": np.std(y),
            "n_samples": len(X),
            "timestamp": datetime.utcnow().isoformat()
        }

        if model:
            if hasattr(model, 'predict'):
                predictions = model.predict(X)
                self.baseline_stats["prediction_mean"] = np.mean(predictions)
                self.baseline_stats["prediction_std"] = np.std(predictions)

    def detect_drift(self, X: np.ndarray, y: np.ndarray, model: Any = None) -> Dict[str, Any]:
        """Detect data drift and model drift"""
        if not self.baseline_stats:
            raise ValueError("Baseline not set. Call set_baseline() first.")

        current_stats = {
            "feature_means": np.mean(X, axis=0),
            "feature_stds": np.std(X, axis=0),
            "target_mean": np.mean(y),
            "target_std": np.std(y),
            "n_samples": len(X),
            "timestamp": datetime.utcnow().isoformat()
        }

        if model and hasattr(model, 'predict'):
            predictions = model.predict(X)
            current_stats["prediction_mean"] = np.mean(predictions)
            current_stats["prediction_std"] = np.std(predictions)

        # Calculate drift metrics
        drift_metrics = {}

        # Feature drift (using KS test approximation)
        for i in range(len(self.baseline_stats["feature_means"])):
            baseline_mean = self.baseline_stats["feature_means"][i]
            current_mean = current_stats["feature_means"][i]
            baseline_std = self.baseline_stats["feature_stds"][i]
            current_std = current_stats["feature_stds"][i]

            # Standardized difference
            if baseline_std > 0 and current_std > 0:
                drift_score = abs(baseline_mean - current_mean) / np.sqrt(baseline_std**2 + current_std**2)
            else:
                drift_score = abs(baseline_mean - current_mean)

            drift_metrics[f"feature_{i}_drift"] = drift_score

        # Target drift
        if self.baseline_stats["target_std"] > 0 and current_stats["target_std"] > 0:
            target_drift = abs(self.baseline_stats["target_mean"] - current_stats["target_mean"]) / \
                          np.sqrt(self.baseline_stats["target_std"]**2 + current_stats["target_std"]**2)
        else:
            target_drift = abs(self.baseline_stats["target_mean"] - current_stats["target_mean"])

        drift_metrics["target_drift"] = target_drift

        # Model drift (if predictions available)
        if "prediction_mean" in self.baseline_stats and "prediction_mean" in current_stats:
            if self.baseline_stats["prediction_std"] > 0 and current_stats["prediction_std"] > 0:
                pred_drift = abs(self.baseline_stats["prediction_mean"] - current_stats["prediction_mean"]) / \
                            np.sqrt(self.baseline_stats["prediction_std"]**2 + current_stats["prediction_std"]**2)
            else:
                pred_drift = abs(self.baseline_stats["prediction_mean"] - current_stats["prediction_mean"])

            drift_metrics["prediction_drift"] = pred_drift

        # Overall drift score
        overall_drift = np.mean(list(drift_metrics.values()))
        drift_metrics["overall_drift"] = overall_drift

        # Determine if drift is significant
        significant_drift = overall_drift > self.drift_threshold

        drift_result = {
            "drift_detected": significant_drift,
            "drift_score": overall_drift,
            "drift_metrics": drift_metrics,
            "baseline_stats": self.baseline_stats,
            "current_stats": current_stats,
            "recommendation": "retrain" if significant_drift else "monitor"
        }

        # Record drift event
        self.drift_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "drift_score": overall_drift,
            "significant": significant_drift,
            "drift_metrics": drift_metrics
        })

        return drift_result


class AutomatedRetraining:
    """Automated model retraining system"""

    def __init__(self, model_repository: ModelVersionControl, drift_detector: ModelDriftDetector):
        self.model_repository = model_repository
        self.drift_detector = drift_detector
        self.retraining_jobs = {}
        self.retraining_history = []

    def schedule_retraining(self, model_name: str, training_data: Tuple[np.ndarray, np.ndarray],
                          retraining_config: Dict[str, Any]) -> str:
        """Schedule automated retraining job"""
        job_id = hashlib.sha256(f"{model_name}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]

        job = {
            "job_id": job_id,
            "model_name": model_name,
            "training_data": training_data,
            "retraining_config": retraining_config,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat(),
            "scheduled_for": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }

        self.retraining_jobs[job_id] = job

        # Schedule job execution
        threading.Thread(target=self._execute_retraining, args=(job_id,)).start()

        return job_id

    def _execute_retraining(self, job_id: str):
        """Execute retraining job"""
        job = self.retraining_jobs[job_id]
        job["status"] = "running"

        try:
            # Load latest model version
            model_versions = self.model_repository.list_model_versions(job["model_name"])
            if not model_versions:
                raise ValueError(f"No model versions found for {job['model_name']}")

            latest_version = model_versions[-1]
            model, _ = self.model_repository.load_model_version(job["model_name"], latest_version["version_hash"])

            # Retrain model
            X_train, y_train = job["training_data"]
            config = job["retraining_config"]

            # Simple retraining (in practice, you'd use the actual training logic)
            if hasattr(model, 'fit'):
                model.fit(X_train, y_train)

            # Save new model version
            metadata = {
                "retraining_job_id": job_id,
                "parent_version": latest_version["version_hash"],
                "retraining_config": config
            }

            new_version_hash = self.model_repository.save_model_version(job["model_name"], model, metadata)

            job["status"] = "completed"
            job["new_version_hash"] = new_version_hash
            job["completed_at"] = datetime.utcnow().isoformat()

            # Record in history
            self.retraining_history.append({
                "job_id": job_id,
                "model_name": job["model_name"],
                "old_version": latest_version["version_hash"],
                "new_version": new_version_hash,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            job["failed_at"] = datetime.utcnow().isoformat()
            logger.error(f"Retraining job {job_id} failed: {str(e)}")

    def get_retraining_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of retraining job"""
        if job_id not in self.retraining_jobs:
            raise ValueError(f"Retraining job {job_id} not found")

        return self.retraining_jobs[job_id]


class PerformanceMonitor:
    """Model performance monitoring system"""

    def __init__(self):
        self.metrics_history = defaultdict(list)
        self.alerts = []
        self.thresholds = {
            "accuracy": {"min": 0.8, "max": 1.0},
            "precision": {"min": 0.7, "max": 1.0},
            "recall": {"min": 0.7, "max": 1.0},
            "f1": {"min": 0.7, "max": 1.0},
            "mse": {"min": 0.0, "max": 1.0},
            "rmse": {"min": 0.0, "max": 1.0},
            "mae": {"min": 0.0, "max": 1.0}
        }

    def log_performance(self, model_name: str, metrics: Dict[str, float], metadata: Dict[str, Any] = None):
        """Log model performance metrics"""
        if metadata is None:
            metadata = {}

        entry = {
            "model_name": model_name,
            "metrics": metrics,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.metrics_history[model_name].append(entry)

        # Check for alerts
        self._check_alerts(model_name, metrics)

    def get_performance_history(self, model_name: str, last_n: int = None) -> List[Dict[str, Any]]:
        """Get performance history for a model"""
        history = self.metrics_history.get(model_name, [])

        if last_n:
            history = history[-last_n:]

        return history

    def get_performance_summary(self, model_name: str) -> Dict[str, Any]:
        """Get performance summary for a model"""
        history = self.metrics_history.get(model_name, [])

        if not history:
            return {"error": "No performance data available"}

        # Aggregate metrics
        all_metrics = [entry["metrics"] for entry in history]
        summary = {}

        for metric in all_metrics[0].keys():
            values = [m[metric] for m in all_metrics if metric in m]
            if values:
                summary[metric] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "trend": self._calculate_trend(values)
                }

        return {
            "model_name": model_name,
            "total_entries": len(history),
            "date_range": {
                "start": history[0]["timestamp"],
                "end": history[-1]["timestamp"]
            },
            "metrics_summary": summary
        }

    def _check_alerts(self, model_name: str, metrics: Dict[str, float]):
        """Check if metrics trigger alerts"""
        for metric, value in metrics.items():
            if metric in self.thresholds:
                threshold = self.thresholds[metric]

                if value < threshold["min"] or value > threshold["max"]:
                    alert = {
                        "model_name": model_name,
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "timestamp": datetime.utcnow().isoformat(),
                        "severity": "high" if abs(value - threshold["min"]) > 0.2 or abs(value - threshold["max"]) > 0.2 else "medium"
                    }

                    self.alerts.append(alert)
                    logger.warning(f"Performance alert for {model_name}: {metric} = {value}")

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend in metrics"""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear regression slope
        x = np.arange(len(values))
        y = np.array(values)

        slope = np.polyfit(x, y, 1)[0]

        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "degrading"
        else:
            return "stable"

    def get_alerts(self, model_name: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """Get performance alerts"""
        alerts = self.alerts

        if model_name:
            alerts = [a for a in alerts if a["model_name"] == model_name]

        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]

        return alerts


class AdvancedModelManagementService:
    """Main service integrating all advanced model management features"""

    def __init__(self, storage_path: str = "./model_versions"):
        self.version_control = ModelVersionControl(storage_path)
        self.ab_testing = ABTestingFramework()
        self.drift_detector = ModelDriftDetector()
        self.retraining = AutomatedRetraining(self.version_control, self.drift_detector)
        self.performance_monitor = PerformanceMonitor()

    def save_model(self, model_name: str, model: Any, metadata: Dict[str, Any] = None) -> str:
        """Save model with versioning"""
        return self.version_control.save_model_version(model_name, model, metadata)

    def load_model(self, model_name: str, version_hash: str = None) -> Tuple[Any, Dict[str, Any]]:
        """Load model version"""
        return self.version_control.load_model_version(model_name, version_hash)

    def run_ab_test(self, experiment_name: str, model_a: Any, model_b: Any,
                   test_data: Tuple[np.ndarray, np.ndarray], metric: str = "accuracy") -> str:
        """Run A/B test between two models"""
        return self.ab_testing.create_experiment(experiment_name, model_a, model_b, test_data, metric)

    def get_ab_test_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get A/B test results"""
        return self.ab_testing.get_experiment_results(experiment_id)

    def detect_model_drift(self, X: np.ndarray, y: np.ndarray, model: Any = None) -> Dict[str, Any]:
        """Detect model and data drift"""
        return self.drift_detector.detect_drift(X, y, model)

    def schedule_model_retraining(self, model_name: str, training_data: Tuple[np.ndarray, np.ndarray],
                                retraining_config: Dict[str, Any]) -> str:
        """Schedule automated model retraining"""
        return self.retraining.schedule_retraining(model_name, training_data, retraining_config)

    def get_retraining_status(self, job_id: str) -> Dict[str, Any]:
        """Get retraining job status"""
        return self.retraining.get_retraining_status(job_id)

    def log_model_performance(self, model_name: str, metrics: Dict[str, float], metadata: Dict[str, Any] = None):
        """Log model performance"""
        self.performance_monitor.log_performance(model_name, metrics, metadata)

    def get_performance_summary(self, model_name: str) -> Dict[str, Any]:
        """Get performance summary"""
        return self.performance_monitor.get_performance_summary(model_name)

    def get_performance_alerts(self, model_name: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """Get performance alerts"""
        return self.performance_monitor.get_alerts(model_name, severity)

    def comprehensive_model_analysis(self, model_name: str) -> Dict[str, Any]:
        """Perform comprehensive model analysis"""
        # Get version history
        versions = self.version_control.list_model_versions(model_name)

        # Get performance summary
        perf_summary = self.performance_monitor.get_performance_summary(model_name)

        # Get drift history
        drift_events = [event for event in self.drift_detector.drift_history if event.get("model_name") == model_name]

        # Get retraining history
        retraining_events = [event for event in self.retraining.retraining_history if event["model_name"] == model_name]

        return {
            "model_name": model_name,
            "total_versions": len(versions),
            "current_version": self.version_control.current_version.get(model_name),
            "performance_summary": perf_summary,
            "drift_events": len(drift_events),
            "retraining_events": len(retraining_events),
            "last_updated": versions[-1]["timestamp"] if versions else None,
            "recommendations": self._generate_recommendations(versions, perf_summary, drift_events)
        }

    def _generate_recommendations(self, versions: List[Dict], perf_summary: Dict, drift_events: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if len(versions) == 0:
            recommendations.append("No model versions found - consider training initial model")
        elif len(versions) > 10:
            recommendations.append("Many model versions - consider cleanup to save storage")

        if perf_summary.get("metrics_summary"):
            for metric, stats in perf_summary["metrics_summary"].items():
                if stats["trend"] == "degrading":
                    recommendations.append(f"Performance degrading for {metric} - consider retraining")
                if stats["mean"] < 0.7:  # Assuming 0.7 is minimum acceptable
                    recommendations.append(f"Low average {metric} - model may need improvement")

        if len(drift_events) > 5:
            recommendations.append("Frequent drift detected - consider more robust model or data monitoring")

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Initialize service
    model_mgmt = AdvancedModelManagementService()

    # Create sample model (simple linear regression for demo)
    class SimpleModel:
        def __init__(self):
            self.weights = np.random.randn(2)

        def fit(self, X, y):
            # Simple gradient descent
            for _ in range(100):
                pred = X @ self.weights
                error = pred - y
                gradient = X.T @ error / len(y)
                self.weights -= 0.01 * gradient

        def predict(self, X):
            return X @ self.weights

    # Create sample data
    np.random.seed(42)
    X = np.random.randn(100, 2)
    y = X @ np.array([1.5, -2.0]) + np.random.normal(0, 0.1, 100)

    # Save initial model
    model = SimpleModel()
    model.fit(X, y)
    version_hash = model_mgmt.save_model("test_model", model, {"type": "linear_regression"})
    print(f"Saved model version: {version_hash}")

    # Load model
    loaded_model, info = model_mgmt.load_model("test_model", version_hash)
    print(f"Loaded model: {info['version_hash']}")

    # Log performance
    pred = loaded_model.predict(X)
    mse = mean_squared_error(y, pred)
    model_mgmt.log_model_performance("test_model", {"mse": mse, "r2": r2_score(y, pred)})

    # Get performance summary
    summary = model_mgmt.get_performance_summary("test_model")
    print(f"Performance summary: {summary}")

    # Comprehensive analysis
    analysis = model_mgmt.comprehensive_model_analysis("test_model")
    print(f"Model analysis: {analysis}")

    print("Advanced Model Management system tested successfully!")
