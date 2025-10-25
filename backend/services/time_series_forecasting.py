import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import statistics

# Check for numpy and pandas availability
try:
    import numpy as np
    import pandas as pd
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("WARNING: NumPy or pandas not available. Time series forecasting will be limited.")

# Import local modules
from services.privacy_ml_integration import PrivacyPreservingMLIntegration, NUMPY_AVAILABLE
from services.machine_learning import PrivacyPreservingML

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeSeriesForecasting:
    """Advanced time series forecasting service for health metrics.
    
    This service provides various forecasting models for health data time series,
    with privacy-preserving capabilities and confidence interval estimation.
    """
    
    def __init__(self, privacy_ml: PrivacyPreservingML = None):
        """Initialize the time series forecasting service.
        
        Args:
            privacy_ml: Optional existing privacy-preserving ML service
        """
        self.privacy_ml = privacy_ml or PrivacyPreservingML()
        self.numpy_available = NUMPY_AVAILABLE
        if not self.numpy_available:
            logger.warning("NumPy not available. Time series forecasting will use basic statistical methods only.")
        self.models = {}
        logger.info("Initialized Time Series Forecasting service")
    
    def forecast_linear(self, 
                      time_series: List[Dict[str, Any]], 
                      horizon: int = 7,
                      privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Generate forecasts using linear regression with privacy guarantees.
        
        Args:
            time_series: List of dictionaries with 'timestamp' and 'value' keys
            horizon: Number of future points to forecast
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            forecast: Forecasted values and confidence intervals
        """
        if len(time_series) < 3:
            return {"success": False, "error": "Insufficient data points for forecasting"}
        
        try:
            # Extract timestamps and values
            timestamps = [item['timestamp'] for item in time_series]
            values = [float(item['value']) for item in time_series]
            
            # Convert timestamps to numeric features (days since first timestamp)
            base_time = datetime.strptime(timestamps[0], "%Y-%m-%d %H:%M:%S")
            x_values = [(datetime.strptime(t, "%Y-%m-%d %H:%M:%S") - base_time).total_seconds() / 86400 
                      for t in timestamps]
            
            # Prepare data for linear regression
            X = np.array(x_values).reshape(-1, 1)
            y = np.array(values)
            
            # Train a private linear model
            model_result = self.privacy_ml.train_private_model("linear", X, y, privacy_budget)
            
            if "coefficients" not in model_result or "intercept" not in model_result:
                return {"success": False, "error": "Failed to train forecasting model"}
            
            # Extract model parameters
            coefficient = model_result["coefficients"][0]
            intercept = model_result["intercept"]
            
            # Generate future timestamps and predictions
            last_x = x_values[-1]
            forecast_x = [last_x + (i+1) for i in range(horizon)]  # Forecast daily intervals
            forecast_values = [coefficient * x + intercept for x in forecast_x]
            
            # Generate forecast timestamps
            last_time = datetime.strptime(timestamps[-1], "%Y-%m-%d %H:%M:%S")
            forecast_timestamps = [(last_time + timedelta(days=i+1)).strftime("%Y-%m-%d %H:%M:%S") 
                                for i in range(horizon)]
            
            # Calculate confidence intervals
            mse = model_result["metrics"].get("mse", 0)
            std_error = np.sqrt(mse) if mse > 0 else 0.1 * np.mean(values)
            confidence_intervals = [{
                "lower": forecast_values[i] - 1.96 * std_error,
                "upper": forecast_values[i] + 1.96 * std_error
            } for i in range(horizon)]
            
            # Store model for future reference
            model_id = str(uuid.uuid4())
            self.models[model_id] = {
                "type": "linear",
                "coefficient": coefficient,
                "intercept": intercept,
                "mse": mse,
                "r2": model_result["metrics"].get("r2", 0),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "model_id": model_id,
                "forecast": [{
                    "timestamp": forecast_timestamps[i],
                    "value": forecast_values[i],
                    "confidence_interval": confidence_intervals[i]
                } for i in range(horizon)],
                "model": {
                    "coefficient": coefficient,
                    "intercept": intercept,
                    "r2": model_result["metrics"].get("r2", 0)
                },
                "privacy_guarantee": model_result.get("privacy_guarantee", {"epsilon": privacy_budget})
            }
            
        except Exception as e:
            logger.error(f"Error in linear forecasting: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def forecast_exponential_smoothing(self, 
                                     time_series: List[Dict[str, Any]], 
                                     horizon: int = 7,
                                     alpha: float = 0.3,
                                     privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Generate forecasts using exponential smoothing with privacy guarantees.
        
        Args:
            time_series: List of dictionaries with 'timestamp' and 'value' keys
            horizon: Number of future points to forecast
            alpha: Smoothing factor (0 < alpha < 1)
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            forecast: Forecasted values and confidence intervals
        """
        if len(time_series) < 3:
            return {"success": False, "error": "Insufficient data points for forecasting"}
        
        try:
            # Extract values
            values = [float(item['value']) for item in time_series]
            timestamps = [item['timestamp'] for item in time_series]
            
            # Apply differential privacy to the input values
            sensitivity = max(values) - min(values) if values else 1.0
            noisy_values = self.privacy_ml.add_noise(values, sensitivity=sensitivity, epsilon=privacy_budget/2)
            
            # Simple exponential smoothing
            level = noisy_values[0]
            smoothed = [level]
            
            for i in range(1, len(noisy_values)):
                level = alpha * noisy_values[i] + (1 - alpha) * level
                smoothed.append(level)
            
            # Generate forecasts
            forecast_values = [level] * horizon  # For simple exponential smoothing, all forecasts are the same
            
            # Generate forecast timestamps
            last_time = datetime.strptime(timestamps[-1], "%Y-%m-%d %H:%M:%S")
            forecast_timestamps = [(last_time + timedelta(days=i+1)).strftime("%Y-%m-%d %H:%M:%S") 
                                for i in range(horizon)]
            
            # Calculate mean squared error for confidence intervals
            errors = [noisy_values[i] - smoothed[i] for i in range(len(smoothed))]
            mse = sum([e**2 for e in errors]) / len(errors) if errors else 0
            std_error = np.sqrt(mse) if mse > 0 else 0.1 * np.mean(values)
            
            # Add noise to std_error for privacy
            noise_scale = sensitivity / (privacy_budget/2)
            private_std_error = std_error + np.random.laplace(0, noise_scale)
            private_std_error = max(private_std_error, 0.01 * np.mean(values))  # Ensure positive
            
            # Calculate confidence intervals with increasing uncertainty over time
            confidence_intervals = [{
                "lower": forecast_values[i] - 1.96 * private_std_error * np.sqrt(i+1),
                "upper": forecast_values[i] + 1.96 * private_std_error * np.sqrt(i+1)
            } for i in range(horizon)]
            
            # Store model for future reference
            model_id = str(uuid.uuid4())
            self.models[model_id] = {
                "type": "exponential_smoothing",
                "alpha": alpha,
                "level": level,
                "mse": mse,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "model_id": model_id,
                "forecast": [{
                    "timestamp": forecast_timestamps[i],
                    "value": forecast_values[i],
                    "confidence_interval": confidence_intervals[i]
                } for i in range(horizon)],
                "model": {
                    "type": "exponential_smoothing",
                    "alpha": alpha,
                    "mse": mse
                },
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in exponential smoothing forecasting: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def forecast_holt_winters(self, 
                           time_series: List[Dict[str, Any]], 
                           horizon: int = 7,
                           seasonal_periods: int = 7,
                           privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Generate forecasts using Holt-Winters method with privacy guarantees.
        
        Args:
            time_series: List of dictionaries with 'timestamp' and 'value' keys
            horizon: Number of future points to forecast
            seasonal_periods: Number of observations per seasonal cycle
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            forecast: Forecasted values and confidence intervals
        """
        if len(time_series) < 2 * seasonal_periods:
            return {"success": False, "error": f"Insufficient data points for forecasting with seasonal period {seasonal_periods}"}
        
        try:
            # Extract values and convert to pandas Series for easier handling
            values = [float(item['value']) for item in time_series]
            timestamps = [item['timestamp'] for item in time_series]
            
            # Apply differential privacy to the input values
            sensitivity = max(values) - min(values) if values else 1.0
            noisy_values = self.privacy_ml.add_noise(values, sensitivity=sensitivity, epsilon=privacy_budget/2)
            
            # Convert to pandas Series for easier handling
            ts = pd.Series(noisy_values)
            
            # Initialize parameters (simplified Holt-Winters)
            alpha = 0.2  # Level smoothing
            beta = 0.1   # Trend smoothing
            gamma = 0.3  # Seasonal smoothing
            
            # Initialize level, trend, and seasonal components
            level = np.mean(ts[:seasonal_periods])
            trend = (np.mean(ts[seasonal_periods:2*seasonal_periods]) - 
                    np.mean(ts[:seasonal_periods])) / seasonal_periods
            
            # Initialize seasonal components
            seasonals = {}
            season_averages = []
            for i in range(seasonal_periods):
                season_averages.append(np.mean([ts[i+j*seasonal_periods] 
                                            for j in range(len(ts)//seasonal_periods)]))
            
            norm = np.mean(season_averages)
            for i in range(seasonal_periods):
                seasonals[i] = season_averages[i] / norm if norm > 0 else 1.0
            
            # Generate forecasts
            forecast_values = []
            for i in range(horizon):
                # Calculate season index
                season_idx = (len(ts) + i) % seasonal_periods
                forecast = (level + (i+1) * trend) * seasonals[season_idx]
                forecast_values.append(forecast)
            
            # Generate forecast timestamps
            last_time = datetime.strptime(timestamps[-1], "%Y-%m-%d %H:%M:%S")
            forecast_timestamps = [(last_time + timedelta(days=i+1)).strftime("%Y-%m-%d %H:%M:%S") 
                                for i in range(horizon)]
            
            # Calculate confidence intervals with increasing uncertainty
            # Use remaining privacy budget for error estimation
            residuals = []
            for i in range(seasonal_periods, len(ts)):
                season_idx = i % seasonal_periods
                expected = (level + trend * (i - seasonal_periods)) * seasonals[season_idx]
                residuals.append(ts[i] - expected)
            
            mse = np.mean([r**2 for r in residuals]) if residuals else 0.1 * np.var(ts)
            std_error = np.sqrt(mse)
            
            # Add noise to std_error for privacy
            noise_scale = sensitivity / (privacy_budget/2)
            private_std_error = std_error + np.random.laplace(0, noise_scale)
            private_std_error = max(private_std_error, 0.01 * np.mean(values))  # Ensure positive
            
            # Calculate confidence intervals with increasing uncertainty over time
            confidence_intervals = [{
                "lower": forecast_values[i] - 1.96 * private_std_error * np.sqrt(i+1),
                "upper": forecast_values[i] + 1.96 * private_std_error * np.sqrt(i+1)
            } for i in range(horizon)]
            
            # Store model for future reference
            model_id = str(uuid.uuid4())
            self.models[model_id] = {
                "type": "holt_winters",
                "level": float(level),
                "trend": float(trend),
                "seasonals": {str(k): float(v) for k, v in seasonals.items()},
                "seasonal_periods": seasonal_periods,
                "mse": float(mse),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "model_id": model_id,
                "forecast": [{
                    "timestamp": forecast_timestamps[i],
                    "value": float(forecast_values[i]),
                    "confidence_interval": confidence_intervals[i]
                } for i in range(horizon)],
                "model": {
                    "type": "holt_winters",
                    "level": float(level),
                    "trend": float(trend),
                    "mse": float(mse),
                    "seasonal_periods": seasonal_periods
                },
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in Holt-Winters forecasting: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def detect_anomalies(self,
                       time_series: List[Dict[str, Any]],
                       method: str = "z_score",
                       threshold: float = 2.0,
                       privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Detect anomalies in time series data with privacy guarantees.
        
        Args:
            time_series: List of dictionaries with 'timestamp' and 'value' keys
            method: Anomaly detection method ('z_score', 'iqr', 'isolation_forest')
            threshold: Threshold for anomaly detection
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            anomalies: Detected anomalies with timestamps and scores
        """
        if len(time_series) < 5:
            return {"success": False, "error": "Insufficient data points for anomaly detection"}
        
        try:
            # Extract values and timestamps
            values = [float(item['value']) for item in time_series]
            timestamps = [item['timestamp'] for item in time_series]
            
            # Apply differential privacy to statistical calculations
            sensitivity = max(values) - min(values) if values else 1.0
            
            anomalies = []
            
            if method == "z_score":
                # Calculate private mean and std
                private_mean = self.privacy_ml.private_mean(values, sensitivity=sensitivity, epsilon=privacy_budget/2)
                
                # Calculate standard deviation with remaining privacy budget
                squared_diffs = [(v - private_mean)**2 for v in values]
                private_variance = self.privacy_ml.private_mean(squared_diffs, 
                                                            sensitivity=sensitivity**2, 
                                                            epsilon=privacy_budget/2)
                private_std = np.sqrt(private_variance) if private_variance > 0 else 0.1 * private_mean
                
                # Detect anomalies
                for i, value in enumerate(values):
                    if private_std > 0:
                        z_score = abs(value - private_mean) / private_std
                        if z_score > threshold:
                            anomalies.append({
                                "timestamp": timestamps[i],
                                "value": value,
                                "score": float(z_score),
                                "threshold": threshold
                            })
                
            elif method == "iqr":
                # Calculate private quartiles
                sorted_values = sorted(values)
                n = len(sorted_values)
                
                # Add noise to quartile positions
                noise_scale = 1.0 / (privacy_budget/3)
                q1_pos = int(n * 0.25 + np.random.laplace(0, noise_scale))
                q2_pos = int(n * 0.5 + np.random.laplace(0, noise_scale))
                q3_pos = int(n * 0.75 + np.random.laplace(0, noise_scale))
                
                # Ensure positions are within bounds
                q1_pos = max(0, min(q1_pos, n-1))
                q2_pos = max(0, min(q2_pos, n-1))
                q3_pos = max(0, min(q3_pos, n-1))
                
                q1 = sorted_values[q1_pos]
                q2 = sorted_values[q2_pos]
                q3 = sorted_values[q3_pos]
                
                iqr = q3 - q1
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                
                # Detect anomalies
                for i, value in enumerate(values):
                    if value < lower_bound or value > upper_bound:
                        score = min(abs(value - lower_bound), abs(value - upper_bound)) / iqr if iqr > 0 else 0
                        anomalies.append({
                            "timestamp": timestamps[i],
                            "value": value,
                            "score": float(score),
                            "threshold": threshold
                        })
                        
            elif method == "isolation_forest":
                # Use the privacy-preserving ML service for isolation forest
                X = np.array(values).reshape(-1, 1)
                
                # Add noise to data for privacy
                noisy_X = self.privacy_ml.add_noise(X, sensitivity=sensitivity, epsilon=privacy_budget)
                
                # Use isolation forest from the ML service
                anomaly_scores = self.privacy_ml.detect_anomalies(noisy_X.flatten(), "isolation_forest")
                
                # Detect anomalies based on scores
                for i, score in enumerate(anomaly_scores):
                    if score > threshold:
                        anomalies.append({
                            "timestamp": timestamps[i],
                            "value": values[i],
                            "score": float(score),
                            "threshold": threshold
                        })
            
            else:
                return {"success": False, "error": f"Unsupported anomaly detection method: {method}"}
            
            return {
                "success": True,
                "anomalies": anomalies,
                "method": method,
                "threshold": threshold,
                "total_points": len(values),
                "anomaly_count": len(anomalies),
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def analyze_seasonality(self,
                          time_series: List[Dict[str, Any]],
                          max_period: int = 30,
                          privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Analyze seasonality patterns in time series data with privacy guarantees.
        
        Args:
            time_series: List of dictionaries with 'timestamp' and 'value' keys
            max_period: Maximum period to check for seasonality
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            seasonality: Detected seasonal patterns and periods
        """
        if len(time_series) < 2 * max_period:
            return {"success": False, "error": f"Insufficient data points for seasonality analysis with max_period={max_period}"}
        
        try:
            # Extract values
            values = [float(item['value']) for item in time_series]
            
            # Apply differential privacy to the input values
            sensitivity = max(values) - min(values) if values else 1.0
            noisy_values = self.privacy_ml.add_noise(values, sensitivity=sensitivity, epsilon=privacy_budget/2)
            
            # Calculate autocorrelation for different lags
            autocorr = []
            mean = np.mean(noisy_values)
            denom = sum([(x - mean) ** 2 for x in noisy_values])
            
            for lag in range(1, min(max_period + 1, len(noisy_values) // 3)):
                numer = sum([(noisy_values[i] - mean) * (noisy_values[i+lag] - mean) 
                           for i in range(len(noisy_values) - lag)])
                if denom > 0:
                    autocorr.append((lag, numer / denom))
                else:
                    autocorr.append((lag, 0))
            
            # Add noise to autocorrelation values for privacy
            noise_scale = 2.0 / (privacy_budget/2 * len(noisy_values))
            private_autocorr = [(lag, corr + np.random.laplace(0, noise_scale)) 
                              for lag, corr in autocorr]
            
            # Find peaks in autocorrelation
            peaks = []
            for i in range(1, len(private_autocorr) - 1):
                if (private_autocorr[i][1] > private_autocorr[i-1][1] and 
                    private_autocorr[i][1] > private_autocorr[i+1][1] and 
                    private_autocorr[i][1] > 0.2):  # Threshold for significance
                    peaks.append(private_autocorr[i])
            
            # Sort peaks by correlation strength
            peaks.sort(key=lambda x: x[1], reverse=True)
            
            # Determine seasonality
            seasonal_periods = [peak[0] for peak in peaks[:3]]  # Top 3 periods
            
            return {
                "success": True,
                "seasonal_periods": seasonal_periods,
                "autocorrelation": [{
                    "lag": lag,
                    "correlation": float(corr)
                } for lag, corr in private_autocorr],
                "peaks": [{
                    "period": lag,
                    "strength": float(corr)
                } for lag, corr in peaks],
                "has_seasonality": len(peaks) > 0,
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in seasonality analysis: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_comprehensive_forecast(self,
                                      time_series: List[Dict[str, Any]],
                                      horizon: int = 7,
                                      privacy_budget: float = 1.0) -> Dict[str, Any]:
        """Generate a comprehensive forecast using multiple methods with privacy guarantees.
        
        Args:
            time_series: List of dictionaries with 'timestamp' and 'value' keys
            horizon: Number of future points to forecast
            privacy_budget: Privacy budget for differential privacy
            
        Returns:
            forecast: Comprehensive forecast with multiple models and insights
        """
        if len(time_series) < 10:
            return {"success": False, "error": "Insufficient data points for comprehensive forecasting"}
        
        try:
            # Split privacy budget across different analyses
            pb_seasonality = privacy_budget * 0.2
            pb_anomalies = privacy_budget * 0.2
            pb_forecasts = privacy_budget * 0.6 / 3  # Split among 3 forecasting methods
            
            # Analyze seasonality first
            seasonality_result = self.analyze_seasonality(time_series, privacy_budget=pb_seasonality)
            has_seasonality = seasonality_result.get("has_seasonality", False)
            seasonal_periods = seasonality_result.get("seasonal_periods", [7])[0] if seasonality_result.get("seasonal_periods") else 7
            
            # Detect anomalies
            anomalies_result = self.detect_anomalies(time_series, privacy_budget=pb_anomalies)
            
            # Generate forecasts using different methods
            linear_forecast = self.forecast_linear(time_series, horizon=horizon, privacy_budget=pb_forecasts)
            exp_forecast = self.forecast_exponential_smoothing(time_series, horizon=horizon, privacy_budget=pb_forecasts)
            
            # Use Holt-Winters if seasonality detected
            hw_forecast = None
            if has_seasonality and len(time_series) >= 2 * seasonal_periods:
                hw_forecast = self.forecast_holt_winters(
                    time_series, horizon=horizon, seasonal_periods=seasonal_periods, privacy_budget=pb_forecasts)
            
            # Combine forecasts (simple average of available forecasts)
            combined_forecast = []
            for i in range(horizon):
                forecasts_at_i = []
                timestamps = []
                
                if linear_forecast.get("success", False):
                    forecasts_at_i.append(linear_forecast["forecast"][i]["value"])
                    timestamps.append(linear_forecast["forecast"][i]["timestamp"])
                    
                if exp_forecast.get("success", False):
                    forecasts_at_i.append(exp_forecast["forecast"][i]["value"])
                    if not timestamps:
                        timestamps.append(exp_forecast["forecast"][i]["timestamp"])
                
                if hw_forecast and hw_forecast.get("success", False):
                    forecasts_at_i.append(hw_forecast["forecast"][i]["value"])
                    if not timestamps:
                        timestamps.append(hw_forecast["forecast"][i]["timestamp"])
                
                if forecasts_at_i:
                    avg_forecast = sum(forecasts_at_i) / len(forecasts_at_i)
                    
                    # Calculate combined confidence interval
                    lower_bounds = []
                    upper_bounds = []
                    
                    if linear_forecast.get("success", False):
                        lower_bounds.append(linear_forecast["forecast"][i]["confidence_interval"]["lower"])
                        upper_bounds.append(linear_forecast["forecast"][i]["confidence_interval"]["upper"])
                        
                    if exp_forecast.get("success", False):
                        lower_bounds.append(exp_forecast["forecast"][i]["confidence_interval"]["lower"])
                        upper_bounds.append(exp_forecast["forecast"][i]["confidence_interval"]["upper"])
                    
                    if hw_forecast and hw_forecast.get("success", False):
                        lower_bounds.append(hw_forecast["forecast"][i]["confidence_interval"]["lower"])
                        upper_bounds.append(hw_forecast["forecast"][i]["confidence_interval"]["upper"])
                    
                    combined_forecast.append({
                        "timestamp": timestamps[0],
                        "value": avg_forecast,
                        "confidence_interval": {
                            "lower": min(lower_bounds) if lower_bounds else avg_forecast * 0.9,
                            "upper": max(upper_bounds) if upper_bounds else avg_forecast * 1.1
                        }
                    })
            
            # Generate insights based on forecasts and analysis
            insights = []
            
            # Trend insight
            if linear_forecast.get("success", False):
                coefficient = linear_forecast["model"]["coefficient"]
                if coefficient > 0.01:
                    insights.append("Upward trend detected in the data")
                elif coefficient < -0.01:
                    insights.append("Downward trend detected in the data")
                else:
                    insights.append("No significant trend detected in the data")
            
            # Seasonality insight
            if has_seasonality:
                insights.append(f"Seasonal pattern detected with period of {seasonal_periods} days")
            else:
                insights.append("No significant seasonal patterns detected")
            
            # Anomaly insight
            if anomalies_result.get("success", False) and anomalies_result.get("anomalies"):
                anomaly_count = len(anomalies_result["anomalies"])
                insights.append(f"Detected {anomaly_count} anomalies in the historical data")
                
                # Check if anomalies are recent
                recent_anomalies = [a for a in anomalies_result["anomalies"] 
                                 if a["timestamp"] in [item["timestamp"] for item in time_series[-3:]]]
                if recent_anomalies:
                    insights.append("Recent anomalies may affect forecast accuracy")
            
            # Forecast stability insight
            if len(combined_forecast) > 0:
                ci_widths = [(f["confidence_interval"]["upper"] - f["confidence_interval"]["lower"]) 
                           for f in combined_forecast]
                avg_width = sum(ci_widths) / len(ci_widths)
                last_value = float(time_series[-1]["value"])
                relative_width = avg_width / abs(last_value) if last_value != 0 else float('inf')
                
                if relative_width < 0.2:
                    insights.append("Forecast has high confidence (narrow confidence intervals)")
                elif relative_width > 0.5:
                    insights.append("Forecast has low confidence (wide confidence intervals)")
            
            return {
                "success": True,
                "forecast": combined_forecast,
                "insights": insights,
                "models": {
                    "linear": linear_forecast.get("model") if linear_forecast.get("success", False) else None,
                    "exponential_smoothing": exp_forecast.get("model") if exp_forecast.get("success", False) else None,
                    "holt_winters": hw_forecast.get("model") if hw_forecast and hw_forecast.get("success", False) else None
                },
                "seasonality": seasonality_result if seasonality_result.get("success", False) else None,
                "anomalies": anomalies_result.get("anomalies", []) if anomalies_result.get("success", False) else [],
                "privacy_guarantee": {"epsilon": privacy_budget}
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive forecasting: {str(e)}")
            return {"success": False, "error": str(e)}