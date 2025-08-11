import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

def calculate_moving_average(values: List[float], window: int = 3) -> List[float]:
    """Calculate moving average with specified window size."""
    if len(values) < window:
        return values
    
    result = []
    for i in range(len(values) - window + 1):
        window_values = values[i:i + window]
        result.append(sum(window_values) / window)
    return result

def predict_next_value(values: List[float], timestamps: List[str]) -> Dict[str, Any]:
    """Predict the next value using simple linear regression."""
    if len(values) < 2:
        return {
            "predicted_value": None,
            "confidence": 0,
            "trend": "insufficient_data"
        }

    # Convert timestamps to hours since first measurement
    base_time = datetime.strptime(timestamps[0], "%Y-%m-%d %H:%M")
    x_values = [(datetime.strptime(t, "%Y-%m-%d %H:%M") - base_time).total_seconds() / 3600 for t in timestamps]
    
    # Calculate means
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(values)
    
    # Calculate slope and intercept
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    
    if denominator == 0:
        return {
            "predicted_value": None,
            "confidence": 0,
            "trend": "stable"
        }
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    # Predict next value (24 hours ahead)
    next_x = x_values[-1] + 24
    predicted_value = slope * next_x + intercept
    
    # Calculate R-squared for confidence
    y_pred = [slope * x + intercept for x in x_values]
    ss_tot = sum((y - y_mean) ** 2 for y in values)
    ss_res = sum((y - yp) ** 2 for y, yp in zip(values, y_pred))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # Determine trend
    trend = "increasing" if slope > 0.1 else "decreasing" if slope < -0.1 else "stable"
    
    return {
        "predicted_value": round(predicted_value, 2),
        "confidence": round(r_squared * 100, 2),
        "trend": trend,
        "next_prediction_time": (datetime.strptime(timestamps[-1], "%Y-%m-%d %H:%M") + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    }

def analyze_patterns(values: List[float], thresholds: Dict[str, float]) -> Dict[str, Any]:
    """Analyze patterns in the data."""
    if len(values) < 3:
        return {
            "patterns": [],
            "variability": 0,
            "stability_score": 0
        }
    
    # Calculate basic statistics
    mean = statistics.mean(values)
    std_dev = statistics.stdev(values)
    
    # Identify patterns
    patterns = []
    
    # Check for high variability
    coefficient_of_variation = (std_dev / mean) * 100
    if coefficient_of_variation > 15:
        patterns.append("high_variability")
    
    # Check for consistent trends
    increases = 0
    decreases = 0
    for i in range(1, len(values)):
        if values[i] > values[i-1]:
            increases += 1
        elif values[i] < values[i-1]:
            decreases += 1
    
    if increases > len(values) * 0.7:
        patterns.append("consistent_increase")
    elif decreases > len(values) * 0.7:
        patterns.append("consistent_decrease")
    
    # Check for out-of-range values
    high_values = sum(1 for v in values if v > thresholds["high"])
    low_values = sum(1 for v in values if v < thresholds["low"])
    
    if high_values > len(values) * 0.3:
        patterns.append("frequent_high_values")
    if low_values > len(values) * 0.3:
        patterns.append("frequent_low_values")
    
    # Calculate stability score (0-100)
    stability_score = 100 - coefficient_of_variation
    stability_score = max(0, min(100, stability_score))
    
    return {
        "patterns": patterns,
        "variability": round(coefficient_of_variation, 2),
        "stability_score": round(stability_score, 2)
    }

def generate_health_insights(values: List[float], timestamps: List[str], metric_type: str) -> Dict[str, Any]:
    """Generate comprehensive health insights for the given metric."""
    if not values or not timestamps:
        return {
            "status": "error",
            "message": "Insufficient data for analysis"
        }
    
    # Define thresholds based on metric type
    thresholds = {
        "blood_sugar": {"low": 70, "high": 140},
        "blood_pressure_systolic": {"low": 90, "high": 120},
        "blood_pressure_diastolic": {"low": 60, "high": 80},
        "heart_rate": {"low": 60, "high": 100}
    }
    
    if metric_type not in thresholds:
        return {
            "status": "error",
            "message": f"Unsupported metric type: {metric_type}"
        }
    
    # Calculate moving averages
    moving_avg = calculate_moving_average(values)
    
    # Get predictions
    prediction = predict_next_value(values, timestamps)
    
    # Analyze patterns
    pattern_analysis = analyze_patterns(values, thresholds[metric_type])
    
    # Generate recommendations
    recommendations = []
    
    if "frequent_high_values" in pattern_analysis["patterns"]:
        if metric_type == "blood_sugar":
            recommendations.append("Consider reviewing diet and medication with healthcare provider")
        elif "blood_pressure" in metric_type:
            recommendations.append("Monitor salt intake and stress levels")
        elif metric_type == "heart_rate":
            recommendations.append("Consider factors affecting heart rate like stress or exercise")
    
    if pattern_analysis["stability_score"] < 60:
        recommendations.append("Increased variability detected. Consider logging factors that might affect readings")
    
    if prediction["trend"] != "stable":
        recommendations.append(f"Trending {prediction['trend']}. Continue monitoring closely")
    
    return {
        "status": "success",
        "moving_average": moving_avg,
        "prediction": prediction,
        "pattern_analysis": pattern_analysis,
        "recommendations": recommendations,
        "summary": {
            "mean": round(statistics.mean(values), 2),
            "median": round(statistics.median(values), 2),
            "std_dev": round(statistics.stdev(values), 2),
            "stability": pattern_analysis["stability_score"]
        }
    } 