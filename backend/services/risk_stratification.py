import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import statistics
import uuid

# Check for numpy availability
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("WARNING: NumPy not available. Risk stratification will be limited.")

# Import local modules
from services.machine_learning import PrivacyPreservingML, NUMPY_AVAILABLE

# Try to import predictive analytics
try:
    from services.predictive_analytics import analyze_patterns
    PREDICTIVE_ANALYTICS_AVAILABLE = True
except ImportError:
    PREDICTIVE_ANALYTICS_AVAILABLE = False
    print("WARNING: Predictive analytics module not available. Some functionality will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskStratificationService:
    """Service for risk stratification of patients based on health metrics.
    
    This service provides privacy-preserving risk assessment capabilities,
    enabling healthcare providers to identify high-risk patients while
    maintaining data privacy.
    """
    
    def __init__(self, privacy_ml: PrivacyPreservingML = None):
        """Initialize the risk stratification service.
        
        Args:
            privacy_ml: Optional existing privacy-preserving ML service
        """
        self.privacy_ml = privacy_ml or PrivacyPreservingML()
        self.numpy_available = NUMPY_AVAILABLE
        if not self.numpy_available:
            logger.warning("NumPy not available. Risk stratification will use basic statistical methods only.")
        self.risk_models = {}
        
        # Default risk thresholds for common health metrics
        self.risk_thresholds = {
            "blood_sugar": {
                "low": 70, 
                "high": 140, 
                "very_high": 200,
                "weight": 0.35
            },
            "blood_pressure_systolic": {
                "low": 90, 
                "high": 140, 
                "very_high": 180,
                "weight": 0.2
            },
            "blood_pressure_diastolic": {
                "low": 60, 
                "high": 90, 
                "very_high": 110,
                "weight": 0.15
            },
            "heart_rate": {
                "low": 60, 
                "high": 100, 
                "very_high": 120,
                "weight": 0.15
            },
            "oxygen_saturation": {
                "low": 92, 
                "high": 100, 
                "very_high": 100,
                "weight": 0.15
            }
        }
        
        logger.info("Initialized Risk Stratification service")
    
    def calculate_risk_score(self, 
                           metrics: Dict[str, List[float]],
                           patient_info: Dict[str, Any] = None,
                           privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Calculate risk score for a patient with privacy guarantees.
        
        Args:
            metrics: Dictionary of health metrics (key: metric name, value: list of values)
            patient_info: Optional additional patient information (age, gender, etc.)
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            risk_assessment: Risk score and stratification
        """
        try:
            # Initialize risk factors for different metrics
            risk_factors = {}
            metric_weights = {}
            total_weight = 0
            
            # Process each metric
            for metric_name, values in metrics.items():
                if not values:
                    continue
                    
                # Determine which threshold to use based on metric name
                threshold_key = None
                for key in self.risk_thresholds.keys():
                    if key in metric_name.lower():
                        threshold_key = key
                        break
                
                if not threshold_key:
                    logger.warning(f"No threshold defined for metric: {metric_name}")
                    continue
                
                thresholds = self.risk_thresholds[threshold_key]
                
                # Apply differential privacy to statistical calculations
                # Split privacy budget among metrics
                metric_privacy_budget = privacy_budget / len(metrics)
                
                private_mean = self.privacy_ml.private_mean(values, epsilon=metric_privacy_budget/2)
                
                # Calculate variability with remaining privacy budget
                if len(values) > 1:
                    squared_diffs = [(v - private_mean)**2 for v in values]
                    private_variance = self.privacy_ml.private_mean(squared_diffs, epsilon=metric_privacy_budget/2)
                    private_std_dev = np.sqrt(private_variance) if private_variance > 0 else 0
                    coefficient_of_variation = (private_std_dev / private_mean) * 100 if private_mean > 0 else 0
                else:
                    coefficient_of_variation = 0
                
                # Calculate risk factor based on metric type
                risk_factor = 0.0
                
                # Special handling for oxygen saturation (higher is better, opposite of other metrics)
                if "oxygen" in metric_name.lower() or "saturation" in metric_name.lower():
                    if private_mean < thresholds["low"]:
                        risk_factor = 1.0  # High risk for low oxygen
                    else:
                        risk_factor = 0.0  # Normal
                else:
                    # For other metrics, check against thresholds
                    if private_mean > thresholds["very_high"]:
                        risk_factor = 1.0  # Very high risk
                    elif private_mean > thresholds["high"]:
                        risk_factor = 0.7  # High risk
                    elif private_mean < thresholds["low"]:
                        risk_factor = 0.5  # Moderate risk (low values)
                    else:
                        risk_factor = 0.0  # Normal
                
                # Add variability component to risk factor
                if coefficient_of_variation > 20:
                    risk_factor = max(risk_factor, 0.8)  # High variability is risky
                elif coefficient_of_variation > 15:
                    risk_factor = max(risk_factor, 0.5)  # Moderate variability
                
                # Store risk factor and weight
                risk_factors[metric_name] = risk_factor
                metric_weights[metric_name] = thresholds.get("weight", 0.1)
                total_weight += metric_weights[metric_name]
            
            # Normalize weights if needed
            if total_weight > 0:
                for metric in metric_weights:
                    metric_weights[metric] /= total_weight
            
            # Calculate overall risk score (weighted average)
            risk_score = 0.0
            for metric_name, risk_factor in risk_factors.items():
                risk_score += risk_factor * metric_weights[metric_name]
            
            # Determine risk category
            risk_category = "low"
            if risk_score >= 0.7:
                risk_category = "high"
            elif risk_score >= 0.4:
                risk_category = "moderate"
            
            # Generate recommendations based on risk factors
            recommendations = []
            for metric_name, risk_factor in risk_factors.items():
                if risk_factor >= 0.7:  # High risk metrics
                    if "blood_sugar" in metric_name.lower():
                        recommendations.append("Monitor blood sugar levels closely and consult healthcare provider")
                    elif "blood_pressure" in metric_name.lower() and "systolic" in metric_name.lower():
                        recommendations.append("Follow up on systolic blood pressure management")
                    elif "blood_pressure" in metric_name.lower() and "diastolic" in metric_name.lower():
                        recommendations.append("Follow up on diastolic blood pressure management")
                    elif "heart_rate" in metric_name.lower():
                        recommendations.append("Evaluate heart rate patterns and consult healthcare provider")
                    elif "oxygen" in metric_name.lower() or "saturation" in metric_name.lower():
                        recommendations.append("Low oxygen saturation detected - seek immediate medical attention")
                    else:
                        recommendations.append(f"Follow up on abnormal {metric_name} readings")
                elif risk_factor >= 0.4:  # Moderate risk metrics
                    recommendations.append(f"Monitor {metric_name} for continued changes")
            
            # Store risk assessment for future reference
            assessment_id = str(uuid.uuid4())
            self.risk_models[assessment_id] = {
                "risk_score": risk_score,
                "risk_category": risk_category,
                "risk_factors": risk_factors,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "assessment_id": assessment_id,
                "risk_score": round(risk_score * 100),  # Convert to 0-100 scale
                "risk_category": risk_category,
                "risk_factors": {k: round(v * 100) for k, v in risk_factors.items()},
                "recommendations": recommendations,
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in risk stratification: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def calculate_population_risk(self,
                               population_metrics: List[Dict[str, List[float]]],
                               privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Calculate risk distribution for a population with privacy guarantees.
        
        Args:
            population_metrics: List of metric dictionaries for multiple patients
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            population_risk: Risk distribution and stratification
        """
        try:
            # Calculate individual risk scores first
            individual_risks = []
            for patient_metrics in population_metrics:
                # Use a small portion of privacy budget for each patient
                patient_privacy_budget = privacy_budget / len(population_metrics)
                risk_result = self.calculate_risk_score(
                    patient_metrics, privacy_budget=patient_privacy_budget)
                
                if risk_result.get("success", False):
                    individual_risks.append({
                        "risk_score": risk_result["risk_score"],
                        "risk_category": risk_result["risk_category"]
                    })
            
            # Calculate distribution of risk categories
            risk_distribution = {
                "high": 0,
                "moderate": 0,
                "low": 0
            }
            
            for risk in individual_risks:
                risk_distribution[risk["risk_category"]] += 1
            
            # Calculate percentages
            total_patients = len(individual_risks)
            risk_percentages = {}
            for category, count in risk_distribution.items():
                risk_percentages[category] = round((count / total_patients) * 100) if total_patients > 0 else 0
            
            # Calculate risk score statistics
            risk_scores = [risk["risk_score"] for risk in individual_risks]
            
            stats = {}
            if risk_scores:
                stats["mean"] = statistics.mean(risk_scores)
                stats["median"] = statistics.median(risk_scores)
                stats["min"] = min(risk_scores)
                stats["max"] = max(risk_scores)
                if len(risk_scores) > 1:
                    stats["std_dev"] = statistics.stdev(risk_scores)
            
            return {
                "success": True,
                "population_size": total_patients,
                "risk_distribution": risk_distribution,
                "risk_percentages": risk_percentages,
                "statistics": stats,
                "high_risk_percentage": risk_percentages.get("high", 0),
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in population risk calculation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def identify_risk_factors(self,
                           metrics: Dict[str, List[float]],
                           timestamps: Dict[str, List[str]] = None,
                           privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Identify specific risk factors and patterns in health metrics.
        
        Args:
            metrics: Dictionary of health metrics (key: metric name, value: list of values)
            timestamps: Optional dictionary of timestamps for each metric
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            risk_factors: Identified risk factors and patterns
        """
        try:
            risk_factors = []
            
            # Process each metric
            for metric_name, values in metrics.items():
                if not values or len(values) < 3:
                    continue
                
                # Allocate privacy budget for this metric
                metric_privacy_budget = privacy_budget / len(metrics)
                
                # Apply differential privacy to values
                sensitivity = max(values) - min(values) if values else 1.0
                noisy_values = self.privacy_ml.add_noise(
                    values, sensitivity=sensitivity, epsilon=metric_privacy_budget/2)
                
                # Analyze patterns in the metric
                metric_timestamps = timestamps.get(metric_name) if timestamps else None
                
                pattern_analysis = analyze_patterns(noisy_values, metric_timestamps)
                
                # Determine which threshold to use based on metric name
                threshold_key = None
                for key in self.risk_thresholds.keys():
                    if key in metric_name.lower():
                        threshold_key = key
                        break
                
                if not threshold_key:
                    continue
                
                thresholds = self.risk_thresholds[threshold_key]
                
                # Check for concerning patterns
                if pattern_analysis.get("consistent_increase", False):
                    risk_factors.append({
                        "metric": metric_name,
                        "pattern": "consistent_increase",
                        "description": f"Consistent increase in {metric_name} values",
                        "severity": "high" if pattern_analysis.get("out_of_range", False) else "moderate"
                    })
                
                if pattern_analysis.get("high_variability", False):
                    risk_factors.append({
                        "metric": metric_name,
                        "pattern": "high_variability",
                        "description": f"High variability in {metric_name} values",
                        "severity": "moderate"
                    })
                
                if pattern_analysis.get("out_of_range", False):
                    # Determine if it's high or low out of range
                    private_mean = self.privacy_ml.private_mean(
                        values, sensitivity=sensitivity, epsilon=metric_privacy_budget/2)
                    
                    if "oxygen" in metric_name.lower() or "saturation" in metric_name.lower():
                        # For oxygen, low is concerning
                        if private_mean < thresholds["low"]:
                            risk_factors.append({
                                "metric": metric_name,
                                "pattern": "low_values",
                                "description": f"Low {metric_name} values detected",
                                "severity": "high"
                            })
                    else:
                        # For other metrics, check both high and low
                        if private_mean > thresholds["very_high"]:
                            risk_factors.append({
                                "metric": metric_name,
                                "pattern": "very_high_values",
                                "description": f"Very high {metric_name} values detected",
                                "severity": "high"
                            })
                        elif private_mean > thresholds["high"]:
                            risk_factors.append({
                                "metric": metric_name,
                                "pattern": "high_values",
                                "description": f"High {metric_name} values detected",
                                "severity": "moderate"
                            })
                        elif private_mean < thresholds["low"]:
                            risk_factors.append({
                                "metric": metric_name,
                                "pattern": "low_values",
                                "description": f"Low {metric_name} values detected",
                                "severity": "moderate"
                            })
            
            # Count risk factors by severity
            severity_counts = {
                "high": 0,
                "moderate": 0,
                "low": 0
            }
            
            for factor in risk_factors:
                severity_counts[factor["severity"]] += 1
            
            return {
                "success": True,
                "risk_factors": risk_factors,
                "severity_counts": severity_counts,
                "total_factors": len(risk_factors),
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in risk factor identification: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_risk_model(self,
                        training_data: List[Dict[str, Any]],
                        features: List[str],
                        target: str = "risk_category",
                        model_type: str = "logistic",
                        privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Create a risk prediction model with privacy guarantees.
        
        Args:
            training_data: List of patient data dictionaries
            features: List of feature names to use for prediction
            target: Target variable to predict
            model_type: Type of model to create ('logistic', 'forest')
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            model: Created risk model information
        """
        try:
            if not training_data or len(training_data) < 10:
                return {"success": False, "error": "Insufficient training data"}
            
            if not features:
                return {"success": False, "error": "No features specified"}
            
            # Extract features and target from training data
            X = []
            y = []
            
            for patient in training_data:
                # Extract feature values
                feature_values = []
                for feature in features:
                    if feature in patient:
                        feature_values.append(float(patient[feature]))
                    else:
                        feature_values.append(0.0)  # Default value if feature is missing
                
                # Extract target value
                target_value = None
                if target in patient:
                    if target == "risk_category":
                        # Convert categorical risk to numeric
                        if patient[target] == "high":
                            target_value = 2
                        elif patient[target] == "moderate":
                            target_value = 1
                        else:  # low
                            target_value = 0
                    else:
                        target_value = float(patient[target])
                
                if target_value is not None and len(feature_values) == len(features):
                    X.append(feature_values)
                    y.append(target_value)
            
            if not X or not y:
                return {"success": False, "error": "Failed to extract features or target from training data"}
            
            # Convert to numpy arrays
            X_array = np.array(X)
            y_array = np.array(y)
            
            # Train a private model
            model_result = self.privacy_ml.train_private_model(model_type, X_array, y_array, privacy_budget)
            
            if not model_result.get("success", False):
                return {"success": False, "error": "Failed to train risk model"}
            
            # Store model for future reference
            model_id = str(uuid.uuid4())
            self.risk_models[model_id] = {
                "type": model_type,
                "features": features,
                "target": target,
                "parameters": model_result.get("coefficients", {}),
                "intercept": model_result.get("intercept", 0),
                "metrics": model_result.get("metrics", {}),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "model_id": model_id,
                "model_type": model_type,
                "features": features,
                "target": target,
                "metrics": model_result.get("metrics", {}),
                "privacy_guarantee": model_result.get("privacy_guarantee", {"epsilon": privacy_budget})
            }
            
        except Exception as e:
            logger.error(f"Error in risk model creation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def predict_risk(self,
                   model_id: str,
                   patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict risk using a previously created risk model.
        
        Args:
            model_id: ID of the risk model to use
            patient_data: Patient data for prediction
            
        Returns:
            prediction: Risk prediction results
        """
        try:
            if model_id not in self.risk_models:
                return {"success": False, "error": "Risk model not found"}
            
            model_info = self.risk_models[model_id]
            features = model_info["features"]
            model_type = model_info["type"]
            
            # Extract feature values
            feature_values = []
            for feature in features:
                if feature in patient_data:
                    feature_values.append(float(patient_data[feature]))
                else:
                    feature_values.append(0.0)  # Default value if feature is missing
            
            # Make prediction based on model type
            prediction = None
            prediction_proba = None
            
            if model_type == "logistic":
                # For logistic regression
                coefficients = model_info["parameters"]
                intercept = model_info["intercept"]
                
                # Calculate logit
                logit = intercept
                for i, value in enumerate(feature_values):
                    logit += coefficients[i] * value
                
                # Apply sigmoid function
                prob = 1 / (1 + np.exp(-logit))
                prediction_proba = prob
                prediction = 2 if prob >= 0.7 else (1 if prob >= 0.4 else 0)
                
            elif model_type == "forest":
                # For random forest, we would need the actual model
                # This is a simplified approximation
                return {"success": False, "error": "Forest model inference not implemented"}
            
            else:
                return {"success": False, "error": f"Unsupported model type: {model_type}"}
            
            # Convert numeric prediction to category
            risk_category = "low"
            if prediction == 2:
                risk_category = "high"
            elif prediction == 1:
                risk_category = "moderate"
            
            # Calculate risk score (0-100)
            risk_score = int(prediction_proba * 100) if prediction_proba is not None else prediction * 50
            
            # Generate recommendations based on risk category
            recommendations = []
            if risk_category == "high":
                recommendations.append("High risk detected - consult healthcare provider")
                recommendations.append("Monitor health metrics closely")
            elif risk_category == "moderate":
                recommendations.append("Moderate risk detected - regular monitoring recommended")
            
            return {
                "success": True,
                "risk_score": risk_score,
                "risk_category": risk_category,
                "probability": round(float(prediction_proba), 3) if prediction_proba is not None else None,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error in risk prediction: {str(e)}")
            return {"success": False, "error": str(e)}