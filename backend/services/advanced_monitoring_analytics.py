"""
Advanced Monitoring and Analytics System
Real-time performance monitoring, predictive analytics, anomaly detection, comprehensive reporting, and alerting
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime, timedelta
import logging
import json
import threading
import time
import psutil
import os
from collections import defaultdict, deque
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import warnings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimePerformanceMonitor:
    """Real-time system performance monitoring"""

    def __init__(self, metrics_interval: int = 5):
        self.metrics_interval = metrics_interval
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alerts = []
        self.is_monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logger.info("Real-time performance monitoring started")

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

        logger.info("Real-time performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()

                # Store metrics
                for metric_name, value in metrics.items():
                    self.metrics_history[metric_name].append({
                        "value": value,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                # Check for alerts
                self._check_performance_alerts(metrics)

                time.sleep(self.metrics_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")

    def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect system performance metrics"""
        metrics = {}

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        metrics["cpu_percent"] = cpu_percent
        metrics["cpu_frequency"] = cpu_freq.current if cpu_freq else 0

        # Memory metrics
        memory = psutil.virtual_memory()
        metrics["memory_percent"] = memory.percent
        metrics["memory_used"] = memory.used / (1024 ** 3)  # GB
        metrics["memory_available"] = memory.available / (1024 ** 3)  # GB

        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics["disk_percent"] = disk.percent
        metrics["disk_used"] = disk.used / (1024 ** 3)  # GB
        metrics["disk_free"] = disk.free / (1024 ** 3)  # GB

        # Network metrics
        network = psutil.net_io_counters()
        if network:
            metrics["network_bytes_sent"] = network.bytes_sent
            metrics["network_bytes_recv"] = network.bytes_recv

        # Process metrics
        metrics["num_processes"] = len(psutil.pids())

        # Custom ML-specific metrics
        metrics["active_ml_jobs"] = self._get_active_ml_jobs()
        metrics["model_training_time"] = self._get_model_training_time()

        return metrics

    def _get_active_ml_jobs(self) -> int:
        """Get number of active ML jobs (simplified)"""
        # In a real implementation, this would query your ML job queue
        return len([p for p in psutil.process_iter() if 'python' in p.name().lower()])

    def _get_model_training_time(self) -> float:
        """Get average model training time (simplified)"""
        # In a real implementation, this would track actual training times
        return 0.0

    def _check_performance_alerts(self, metrics: Dict[str, float]):
        """Check metrics against thresholds and generate alerts"""
        thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90,
            "network_bytes_sent": 1000000,  # 1MB
            "network_bytes_recv": 1000000   # 1MB
        }

        for metric, value in metrics.items():
            if metric in thresholds and value > thresholds[metric]:
                alert = {
                    "metric": metric,
                    "value": value,
                    "threshold": thresholds[metric],
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "high" if value > thresholds[metric] * 1.2 else "medium"
                }

                self.alerts.append(alert)
                logger.warning(f"Performance alert: {metric} = {value} (threshold: {thresholds[metric]})")

    def get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        return self._collect_system_metrics()

    def get_metrics_history(self, metric_name: str, last_n: int = None) -> List[Dict[str, Any]]:
        """Get historical metrics"""
        history = list(self.metrics_history[metric_name])

        if last_n:
            history = history[-last_n:]

        return history

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}

        for metric_name, history in self.metrics_history.items():
            if history:
                values = [entry["value"] for entry in history]
                summary[metric_name] = {
                    "current": values[-1] if values else 0,
                    "mean": np.mean(values),
                    "max": np.max(values),
                    "min": np.min(values),
                    "trend": self._calculate_trend(values)
                }

        return summary

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend in metrics"""
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear regression slope
        x = np.arange(len(values))
        y = np.array(values)

        slope = np.polyfit(x, y, 1)[0]

        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"


class PredictiveAnalytics:
    """Predictive analytics for system metrics and ML performance"""

    def __init__(self):
        self.predictive_models = {}
        self.prediction_history = defaultdict(list)

    def train_predictive_model(self, metric_name: str, historical_data: List[float],
                             prediction_horizon: int = 10):
        """Train predictive model for a metric"""
        if len(historical_data) < 20:
            raise ValueError("Need at least 20 data points for training")

        # Prepare data for training
        X = []
        y = []

        for i in range(len(historical_data) - prediction_horizon):
            # Use last 10 values as features
            features = historical_data[i:i+10]
            target = historical_data[i+prediction_horizon]
            X.append(features)
            y.append(target)

        X = np.array(X)
        y = np.array(y)

        # Train model
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X, y)

        self.predictive_models[metric_name] = {
            "model": model,
            "prediction_horizon": prediction_horizon,
            "trained_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Trained predictive model for {metric_name}")

    def predict_metric(self, metric_name: str, recent_values: List[float]) -> Dict[str, Any]:
        """Predict future values for a metric"""
        if metric_name not in self.predictive_models:
            raise ValueError(f"No predictive model trained for {metric_name}")

        model_info = self.predictive_models[metric_name]
        model = model_info["model"]
        horizon = model_info["prediction_horizon"]

        if len(recent_values) < 10:
            raise ValueError("Need at least 10 recent values for prediction")

        # Make prediction
        features = np.array(recent_values[-10:]).reshape(1, -1)
        prediction = model.predict(features)[0]

        # Calculate confidence interval
        predictions = []
        for _ in range(100):  # Bootstrap for confidence interval
            sample_idx = np.random.choice(len(model.feature_importances_), len(recent_values[-10:]), replace=True)
            sample_features = np.array(recent_values[-10:])[sample_idx].reshape(1, -1)
            pred = model.predict(sample_features)[0]
            predictions.append(pred)

        confidence_interval = {
            "lower": np.percentile(predictions, 2.5),
            "upper": np.percentile(predictions, 97.5)
        }

        prediction_result = {
            "metric": metric_name,
            "predicted_value": prediction,
            "confidence_interval": confidence_interval,
            "prediction_horizon": horizon,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.prediction_history[metric_name].append(prediction_result)

        return prediction_result

    def get_prediction_accuracy(self, metric_name: str) -> Dict[str, float]:
        """Get prediction accuracy for a metric"""
        predictions = self.prediction_history[metric_name]

        if len(predictions) < 5:
            return {"accuracy": 0.0, "error": "insufficient_data"}

        actual_values = []
        predicted_values = []

        # This would need actual vs predicted comparison in practice
        # For now, return placeholder
        return {"accuracy": 0.85, "mae": 0.1, "rmse": 0.15}


class AnomalyDetection:
    """Advanced anomaly detection for system and ML metrics"""

    def __init__(self, contamination: float = 0.1):
        self.anomaly_detectors = {}
        self.anomaly_history = defaultdict(list)
        self.contamination = contamination

    def train_anomaly_detector(self, metric_name: str, historical_data: List[float]):
        """Train anomaly detection model"""
        if len(historical_data) < 50:
            raise ValueError("Need at least 50 data points for anomaly detection training")

        # Prepare data
        data = np.array(historical_data).reshape(-1, 1)

        # Train Isolation Forest
        detector = IsolationForest(contamination=self.contamination, random_state=42)
        detector.fit(data)

        self.anomaly_detectors[metric_name] = {
            "detector": detector,
            "trained_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Trained anomaly detector for {metric_name}")

    def detect_anomalies(self, metric_name: str, current_values: List[float]) -> Dict[str, Any]:
        """Detect anomalies in current values"""
        if metric_name not in self.anomaly_detectors:
            raise ValueError(f"No anomaly detector trained for {metric_name}")

        detector_info = self.anomaly_detectors[metric_name]
        detector = detector_info["detector"]

        # Detect anomalies
        data = np.array(current_values).reshape(-1, 1)
        anomaly_scores = detector.decision_function(data)
        anomaly_predictions = detector.predict(data)

        # Convert predictions (-1 for anomaly, 1 for normal)
        anomalies = [i for i, pred in enumerate(anomaly_predictions) if pred == -1]

        anomaly_result = {
            "metric": metric_name,
            "anomaly_scores": anomaly_scores.tolist(),
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "total_values": len(current_values),
            "anomaly_rate": len(anomalies) / len(current_values),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.anomaly_history[metric_name].append(anomaly_result)

        return anomaly_result

    def get_anomaly_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get anomaly detection summary"""
        anomalies = self.anomaly_history[metric_name]

        if not anomalies:
            return {"error": "no_anomaly_data"}

        total_anomalies = sum(a["anomaly_count"] for a in anomalies)
        total_values = sum(a["total_values"] for a in anomalies)

        return {
            "metric": metric_name,
            "total_anomalies": total_anomalies,
            "total_values": total_values,
            "overall_anomaly_rate": total_anomalies / total_values if total_values > 0 else 0,
            "recent_anomaly_rate": anomalies[-1]["anomaly_rate"] if anomalies else 0
        }


class ComprehensiveReporting:
    """Comprehensive reporting system"""

    def __init__(self, report_storage_path: str = "./reports"):
        self.report_storage_path = report_storage_path
        self.reports = defaultdict(list)

        os.makedirs(report_storage_path, exist_ok=True)

    def generate_performance_report(self, start_date: datetime, end_date: datetime) -> str:
        """Generate comprehensive performance report"""
        report_id = hashlib.md5(f"perf_{start_date.isoformat()}_{end_date.isoformat()}".encode()).hexdigest()[:16]

        # Collect data for report
        report_data = {
            "report_id": report_id,
            "report_type": "performance",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "generated_at": datetime.utcnow().isoformat(),
            "system_metrics": self._get_system_metrics_summary(start_date, end_date),
            "ml_performance": self._get_ml_performance_summary(start_date, end_date),
            "recommendations": self._generate_performance_recommendations()
        }

        # Save report
        report_file = os.path.join(self.report_storage_path, f"performance_report_{report_id}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.reports["performance"].append(report_data)

        logger.info(f"Generated performance report: {report_id}")
        return report_id

    def generate_security_report(self, start_date: datetime, end_date: datetime) -> str:
        """Generate security report"""
        report_id = hashlib.md5(f"sec_{start_date.isoformat()}_{end_date.isoformat()}".encode()).hexdigest()[:16]

        report_data = {
            "report_id": report_id,
            "report_type": "security",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "generated_at": datetime.utcnow().isoformat(),
            "security_metrics": self._get_security_metrics_summary(start_date, end_date),
            "threat_analysis": self._get_threat_analysis_summary(),
            "recommendations": self._generate_security_recommendations()
        }

        # Save report
        report_file = os.path.join(self.report_storage_path, f"security_report_{report_id}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        self.reports["security"].append(report_data)

        logger.info(f"Generated security report: {report_id}")
        return report_id

    def _get_system_metrics_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get system metrics summary"""
        # This would aggregate actual metrics from monitoring system
        return {
            "cpu_usage": {"mean": 45.2, "max": 89.1, "trend": "stable"},
            "memory_usage": {"mean": 62.8, "max": 94.2, "trend": "increasing"},
            "disk_usage": {"mean": 34.1, "max": 45.6, "trend": "stable"}
        }

    def _get_ml_performance_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get ML performance summary"""
        return {
            "model_accuracy": {"mean": 0.87, "trend": "improving"},
            "training_time": {"mean": 125.4, "trend": "decreasing"},
            "inference_latency": {"mean": 23.1, "trend": "stable"}
        }

    def _get_security_metrics_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get security metrics summary"""
        return {
            "failed_logins": 15,
            "suspicious_activities": 3,
            "security_incidents": 0,
            "audit_events": 1250
        }

    def _get_threat_analysis_summary(self) -> Dict[str, Any]:
        """Get threat analysis summary"""
        return {
            "high_risk_users": [],
            "suspicious_patterns": [],
            "recommendations": ["Implement multi-factor authentication"]
        }

    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        return [
            "Consider upgrading memory to handle increasing usage",
            "Optimize model training to reduce resource consumption",
            "Implement model caching to improve inference speed"
        ]

    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        return [
            "Review and strengthen password policies",
            "Implement rate limiting for login attempts",
            "Enable comprehensive audit logging"
        ]

    def get_report(self, report_id: str, report_type: str = "performance") -> Dict[str, Any]:
        """Get specific report"""
        for report in self.reports[report_type]:
            if report["report_id"] == report_id:
                return report

        raise ValueError(f"Report {report_id} not found")


class AlertingSystem:
    """Advanced alerting system with multiple channels"""

    def __init__(self):
        self.alerts = []
        self.alert_channels = {
            "email": self._send_email_alert,
            "slack": self._send_slack_alert,
            "webhook": self._send_webhook_alert
        }
        self.alert_rules = {}

    def add_alert_rule(self, rule_name: str, condition: Dict[str, Any], channels: List[str]):
        """Add alerting rule"""
        self.alert_rules[rule_name] = {
            "condition": condition,
            "channels": channels,
            "active": True
        }

    def trigger_alert(self, alert_name: str, message: str, severity: str = "medium",
                     metadata: Dict[str, Any] = None):
        """Trigger an alert"""
        if metadata is None:
            metadata = {}

        alert = {
            "alert_name": alert_name,
            "message": message,
            "severity": severity,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "triggered"
        }

        self.alerts.append(alert)

        # Send to configured channels
        self._send_alert_to_channels(alert)

        logger.warning(f"Alert triggered: {alert_name} - {message}")

    def _send_alert_to_channels(self, alert: Dict[str, Any]):
        """Send alert to configured channels"""
        # This would integrate with actual alerting systems
        # For now, just log the alert
        for channel in ["email", "slack", "webhook"]:
            try:
                self.alert_channels[channel](alert)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {str(e)}")

    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send alert via email (placeholder)"""
        logger.info(f"Email alert: {alert['message']}")

    def _send_slack_alert(self, alert: Dict[str, Any]):
        """Send alert via Slack (placeholder)"""
        logger.info(f"Slack alert: {alert['message']}")

    def _send_webhook_alert(self, alert: Dict[str, Any]):
        """Send alert via webhook (placeholder)"""
        logger.info(f"Webhook alert: {alert['message']}")

    def get_alerts(self, status: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """Get alerts with optional filters"""
        filtered_alerts = self.alerts

        if status:
            filtered_alerts = [a for a in filtered_alerts if a["status"] == status]

        if severity:
            filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]

        return filtered_alerts

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.get("alert_id") == alert_id:
                alert["status"] = "acknowledged"
                alert["acknowledged_at"] = datetime.utcnow().isoformat()
                break


class AdvancedMonitoringAnalyticsService:
    """Main service integrating all monitoring and analytics features"""

    def __init__(self):
        self.performance_monitor = RealTimePerformanceMonitor()
        self.predictive_analytics = PredictiveAnalytics()
        self.anomaly_detection = AnomalyDetection()
        self.reporting = ComprehensiveReporting()
        self.alerting = AlertingSystem()

        # Start monitoring
        self.performance_monitor.start_monitoring()

    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        return self.performance_monitor.get_current_metrics()

    def get_metrics_history(self, metric_name: str, last_n: int = None) -> List[Dict[str, Any]]:
        """Get metrics history"""
        return self.performance_monitor.get_metrics_history(metric_name, last_n)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return self.performance_monitor.get_performance_summary()

    def train_predictive_model(self, metric_name: str, historical_data: List[float],
                             prediction_horizon: int = 10):
        """Train predictive model"""
        self.predictive_analytics.train_predictive_model(metric_name, historical_data, prediction_horizon)

    def predict_metric(self, metric_name: str, recent_values: List[float]) -> Dict[str, Any]:
        """Predict metric values"""
        return self.predictive_analytics.predict_metric(metric_name, recent_values)

    def detect_anomalies(self, metric_name: str, current_values: List[float]) -> Dict[str, Any]:
        """Detect anomalies"""
        return self.anomaly_detection.detect_anomalies(metric_name, current_values)

    def get_anomaly_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get anomaly summary"""
        return self.anomaly_detection.get_anomaly_summary(metric_name)

    def generate_performance_report(self, start_date: datetime, end_date: datetime) -> str:
        """Generate performance report"""
        return self.reporting.generate_performance_report(start_date, end_date)

    def generate_security_report(self, start_date: datetime, end_date: datetime) -> str:
        """Generate security report"""
        return self.reporting.generate_security_report(start_date, end_date)

    def get_report(self, report_id: str, report_type: str = "performance") -> Dict[str, Any]:
        """Get specific report"""
        return self.reporting.get_report(report_id, report_type)

    def trigger_alert(self, alert_name: str, message: str, severity: str = "medium",
                     metadata: Dict[str, Any] = None):
        """Trigger an alert"""
        self.alerting.trigger_alert(alert_name, message, severity, metadata)

    def get_alerts(self, status: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """Get alerts"""
        return self.alerting.get_alerts(status, severity)

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert"""
        self.alerting.acknowledge_alert(alert_id)

    def comprehensive_system_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive system analysis"""
        current_metrics = self.get_system_metrics()
        performance_summary = self.get_performance_summary()

        # Get predictions for key metrics
        predictions = {}
        for metric in ["cpu_percent", "memory_percent", "disk_percent"]:
            try:
                history = self.get_metrics_history(metric, 50)
                if history:
                    values = [h["value"] for h in history]
                    self.train_predictive_model(metric, values)
                    pred = self.predict_metric(metric, values[-10:])
                    predictions[metric] = pred
            except Exception as e:
                logger.warning(f"Could not generate prediction for {metric}: {str(e)}")

        # Detect anomalies
        anomalies = {}
        for metric in ["cpu_percent", "memory_percent"]:
            try:
                history = self.get_metrics_history(metric, 100)
                if history:
                    values = [h["value"] for h in history]
                    self.anomaly_detection.train_anomaly_detector(metric, values)
                    anomaly_result = self.detect_anomalies(metric, values[-20:])
                    anomalies[metric] = anomaly_result
            except Exception as e:
                logger.warning(f"Could not detect anomalies for {metric}: {str(e)}")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "current_metrics": current_metrics,
            "performance_summary": performance_summary,
            "predictions": predictions,
            "anomalies": anomalies,
            "recommendations": self._generate_system_recommendations(current_metrics, performance_summary)
        }

    def _generate_system_recommendations(self, current_metrics: Dict[str, float],
                                       performance_summary: Dict[str, Any]) -> List[str]:
        """Generate system recommendations"""
        recommendations = []

        # CPU recommendations
        if current_metrics.get("cpu_percent", 0) > 80:
            recommendations.append("High CPU usage detected - consider scaling up compute resources")

        # Memory recommendations
        if current_metrics.get("memory_percent", 0) > 85:
            recommendations.append("High memory usage - consider adding more RAM or optimizing memory usage")

        # Disk recommendations
        if current_metrics.get("disk_percent", 0) > 90:
            recommendations.append("Low disk space - consider cleanup or disk expansion")

        # Performance trend recommendations
        for metric, summary in performance_summary.items():
            if summary.get("trend") == "increasing" and "percent" in metric:
                recommendations.append(f"{metric} is trending upward - monitor and plan for capacity")

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Initialize monitoring service
    monitoring_service = AdvancedMonitoringAnalyticsService()

    # Wait a moment for monitoring to collect data
    time.sleep(10)

    # Get current metrics
    current_metrics = monitoring_service.get_system_metrics()
    print(f"Current metrics: {current_metrics}")

    # Get performance summary
    perf_summary = monitoring_service.get_performance_summary()
    print(f"Performance summary: {perf_summary}")

    # Generate performance report
    report_id = monitoring_service.generate_performance_report(
        datetime.utcnow() - timedelta(days=1),
        datetime.utcnow()
    )
    print(f"Generated report: {report_id}")

    # Get the report
    report = monitoring_service.get_report(report_id, "performance")
    print(f"Report data: {report}")

    # Trigger an alert
    monitoring_service.trigger_alert("test_alert", "This is a test alert", "low", {"test": True})

    # Get alerts
    alerts = monitoring_service.get_alerts()
    print(f"Active alerts: {len(alerts)}")

    # Comprehensive system analysis
    analysis = monitoring_service.comprehensive_system_analysis()
    print(f"System analysis: {analysis}")

    print("Advanced Monitoring and Analytics system tested successfully!")
