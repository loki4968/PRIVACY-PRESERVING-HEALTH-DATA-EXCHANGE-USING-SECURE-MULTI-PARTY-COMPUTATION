import os
import csv
import json
import hashlib
import re
from typing import Dict, List, Union, Optional, Tuple, Any
from datetime import datetime
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, VALID_CATEGORIES
import statistics
import math
from services.predictive_analytics import generate_health_insights

class FileValidationError(Exception):
    pass

def allowed_file_extension(filename: str) -> bool:
    """Check if the file extension is allowed."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def validate_file_size(file) -> bool:
    """Check if the file size is within limits."""
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    return size <= MAX_FILE_SIZE

def get_file_size(file) -> int:
    """Get the file size in bytes."""
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    return size

def validate_category(category: str) -> bool:
    """Check if the category is valid."""
    return category in VALID_CATEGORIES

def hash_file_content(file_path: str) -> str:
    """Generate SHA-256 hash of file content."""
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        return hashlib.sha256(file_bytes).hexdigest()

def safe_float_conversion(value: str) -> Optional[float]:
    """Safely convert string to float."""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None

def analyze_trends(data: List[float]) -> Dict[str, Any]:
    """Analyze trends in health metrics over time."""
    if len(data) < 2:
        return None
    
    # Calculate basic trend
    first_value = data[0]
    last_value = data[-1]
    total_change = ((last_value - first_value) / first_value) * 100
    
    return {
        'trend': 'increasing' if last_value > first_value else 'decreasing',
        'percent_change': float(total_change)
    }

def analyze_health_metrics(values: List[float], metric_type: str) -> Dict[str, Any]:
    """Analyze health metrics and provide insights."""
    if not values:
        return {
            "min": 0,
            "max": 0,
            "average": 0,
            "median": 0,
            "std_dev": 0,
            "count": 0,
            "insights": {
                "normal_range": "No data",
                "status": "No data",
                "recommendation": "No data available for analysis"
            }
        }
    
    try:
        stats = {
            "min": float(min(values)),
            "max": float(max(values)),
            "average": float(round(statistics.mean(values), 2)),
            "median": float(round(statistics.median(values), 2)),
            "std_dev": float(round(statistics.stdev(values), 2)) if len(values) > 1 else 0,
            "count": len(values)
        }
    except (TypeError, ValueError) as e:
        print(f"Error calculating statistics: {str(e)}")
        return {
            "min": 0,
            "max": 0,
            "average": 0,
            "median": 0,
            "std_dev": 0,
            "count": len(values),
            "error": f"Error calculating statistics: {str(e)}"
        }
    
    # Add health-specific insights
    if metric_type == "blood sugar level":
        stats["insights"] = {
            "normal_range": "70-140 mg/dL",
            "status": "Normal" if 70 <= stats["average"] <= 140 else "Out of range",
            "recommendation": get_blood_sugar_recommendation(stats["average"])
        }
    elif metric_type == "systolic blood pressure":
        stats["insights"] = {
            "normal_range": "90-120 mmHg",
            "status": get_blood_pressure_status(stats["average"], 80),  # Using 80 as default diastolic
            "recommendation": get_blood_pressure_recommendation(stats["average"], 80)
        }
    elif metric_type == "diastolic blood pressure":
        stats["insights"] = {
            "normal_range": "60-80 mmHg",
            "status": get_blood_pressure_status(120, stats["average"]),  # Using 120 as default systolic
            "recommendation": get_blood_pressure_recommendation(120, stats["average"])
        }
    elif metric_type == "heart rate":
        stats["insights"] = {
            "normal_range": "60-100 bpm",
            "status": "Normal" if 60 <= stats["average"] <= 100 else "Out of range",
            "recommendation": get_heart_rate_recommendation(stats["average"])
        }
    elif metric_type == "temperature":
        stats["insights"] = {
            "normal_range": "97.8-99.1°F",
            "status": "Normal" if 97.8 <= stats["average"] <= 99.1 else "Out of range",
            "recommendation": get_temperature_recommendation(stats["average"])
        }
    elif metric_type == "hemoglobin":
        stats["insights"] = {
            "normal_range": "12-17 g/dL",
            "status": "Normal" if 12 <= stats["average"] <= 17 else "Out of range",
            "recommendation": "Consult healthcare provider for detailed analysis"
        }
    elif metric_type == "white blood cells":
        stats["insights"] = {
            "normal_range": "4,500-11,000 cells/µL",
            "status": "Normal" if 4500 <= stats["average"] <= 11000 else "Out of range",
            "recommendation": "Consult healthcare provider for detailed analysis"
        }
    elif metric_type == "red blood cells":
        stats["insights"] = {
            "normal_range": "4.5-5.9 million/µL",
            "status": "Normal" if 4.5 <= stats["average"] <= 5.9 else "Out of range",
            "recommendation": "Consult healthcare provider for detailed analysis"
        }
    elif metric_type == "platelets":
        stats["insights"] = {
            "normal_range": "150,000-450,000/µL",
            "status": "Normal" if 150000 <= stats["average"] <= 450000 else "Out of range",
            "recommendation": "Consult healthcare provider for detailed analysis"
        }
    else:
        stats["insights"] = {
            "normal_range": "Unknown",
            "status": "Unknown",
            "recommendation": "Consult healthcare provider for interpretation"
        }
    
    # Ensure all numeric values are properly formatted
    for key in ["min", "max", "average", "median", "std_dev"]:
        if key in stats:
            try:
                stats[key] = float(round(stats[key], 2))
            except (TypeError, ValueError):
                stats[key] = 0.0
    
    return stats

def get_blood_sugar_recommendation(avg_level: float) -> str:
    if avg_level < 70:
        return "Blood sugar is low. Consider having a quick source of glucose."
    elif avg_level > 140:
        return "Blood sugar is high. Monitor diet and consult healthcare provider."
    else:
        return "Blood sugar levels are within normal range. Maintain current diet and exercise routine."

def get_blood_pressure_status(systolic: float, diastolic: float) -> str:
    if systolic < 90 or diastolic < 60:
        return "Low Blood Pressure"
    elif systolic < 120 and diastolic < 80:
        return "Normal"
    elif systolic < 130 and diastolic < 80:
        return "Elevated"
    elif systolic < 140 or diastolic < 90:
        return "Stage 1 Hypertension"
    else:
        return "Stage 2 Hypertension"

def get_blood_pressure_recommendation(systolic: float, diastolic: float) -> str:
    status = get_blood_pressure_status(systolic, diastolic)
    recommendations = {
        "Low Blood Pressure": "Increase fluid intake and consult healthcare provider.",
        "Normal": "Maintain healthy lifestyle with regular exercise and balanced diet.",
        "Elevated": "Consider lifestyle changes and monitor regularly.",
        "Stage 1 Hypertension": "Implement lifestyle changes and consult healthcare provider.",
        "Stage 2 Hypertension": "Seek immediate medical attention and follow prescribed treatment."
    }
    return recommendations.get(status, "Consult healthcare provider for personalized advice.")

def get_heart_rate_recommendation(avg_rate: float) -> str:
    if avg_rate < 60:
        return "Heart rate is low. If experiencing symptoms, consult healthcare provider."
    elif avg_rate > 100:
        return "Heart rate is elevated. Monitor stress levels and physical activity."
    else:
        return "Heart rate is within normal range. Maintain current activity level."

def get_temperature_recommendation(avg_temp: float) -> str:
    if avg_temp < 97.8:
        return "Temperature is low. Monitor for symptoms and stay warm."
    elif avg_temp > 99.1:
        return "Temperature is elevated. Monitor for fever symptoms."
    else:
        return "Temperature is within normal range."

def analyze_blood_sugar_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze blood sugar data with advanced statistical analysis."""
    results = {
        "status": "success",
        "category": "blood_sugar",
        "analysis": {},
        "patient_analysis": {},
        "overall_insights": {},
        "metadata": {
            "total_records": len(data),
            "date_range": {
                "start": data[0].get("Date", ""),
                "end": data[-1].get("Date", "")
            },
            "notes": []
        },
        "format_type": "blood_sugar",
        "file_metadata": {
            "columns": list(data[0].keys())
        }
    }
    
    # Group data by patient
    patients_data = {}
    for row in data:
        patient_id = row.get("PatientID")
        if not patient_id:
            continue
            
        if patient_id not in patients_data:
            patients_data[patient_id] = []
        
        try:
            blood_sugar = float(row.get("BloodSugar_mg_dL", 0))
            date_str = row.get("Date", "")
            time_str = row.get("Time", "")
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            patients_data[patient_id].append({
                "blood_sugar": blood_sugar,
                "timestamp": timestamp,
                "raw_data": row
            })
        except (ValueError, TypeError) as e:
            print(f"Error processing row for patient {patient_id}: {e}")
            continue
    
    # Analyze each patient's data
    for patient_id, patient_data in patients_data.items():
        if len(patient_data) < 2:
            continue
            
        # Sort data by timestamp
        patient_data.sort(key=lambda x: x["timestamp"])
        blood_sugar_values = [d["blood_sugar"] for d in patient_data]
        timestamps = [d["timestamp"].strftime("%Y-%m-%d %H:%M") for d in patient_data]
        
        # Get predictive insights
        insights = generate_health_insights(blood_sugar_values, timestamps, "blood_sugar")
        
        # Basic statistics
        stats = {
            "min": float(min(blood_sugar_values)),
            "max": float(max(blood_sugar_values)),
            "average": float(round(statistics.mean(blood_sugar_values), 2)),
            "median": float(round(statistics.median(blood_sugar_values), 2)),
            "std_dev": float(round(statistics.stdev(blood_sugar_values), 2)),
            "count": len(blood_sugar_values)
        }
        
        # Trend Analysis
        first_value = blood_sugar_values[0]
        last_value = blood_sugar_values[-1]
        total_change = ((last_value - first_value) / first_value) * 100
        
        # Moving average to detect patterns
        window_size = min(3, len(blood_sugar_values))
        moving_averages = []
        for i in range(len(blood_sugar_values) - window_size + 1):
            window = blood_sugar_values[i:i + window_size]
            moving_averages.append(sum(window) / window_size)
        
        # Detect anomalies (values outside 2 standard deviations)
        mean = statistics.mean(blood_sugar_values)
        std_dev = statistics.stdev(blood_sugar_values)
        anomaly_threshold = 2 * std_dev
        anomalies = []
        anomaly_indices = []
        for i, value in enumerate(blood_sugar_values):
            if abs(value - mean) > anomaly_threshold:
                anomalies.append(value)
                anomaly_indices.append(i)
        
        # Pattern Analysis
        if len(blood_sugar_values) >= 3:
            # Identify patterns based on ranges
            low_threshold = 70
            high_threshold = 140
            patterns = []
            for value in blood_sugar_values:
                if value < low_threshold:
                    patterns.append("Low")
                elif value > high_threshold:
                    patterns.append("High")
                else:
                    patterns.append("Normal")
            
            # Calculate pattern centers
            pattern_centers = {
                "Low": statistics.mean([v for v, p in zip(blood_sugar_values, patterns) if p == "Low"]) if any(p == "Low" for p in patterns) else None,
                "Normal": statistics.mean([v for v, p in zip(blood_sugar_values, patterns) if p == "Normal"]) if any(p == "Normal" for p in patterns) else None,
                "High": statistics.mean([v for v, p in zip(blood_sugar_values, patterns) if p == "High"]) if any(p == "High" for p in patterns) else None
            }
            pattern_centers = {k: float(v) for k, v in pattern_centers.items() if v is not None}
        else:
            patterns = None
            pattern_centers = None
        
        # Risk Assessment
        high_readings = sum(1 for v in blood_sugar_values if v > 140)
        low_readings = sum(1 for v in blood_sugar_values if v < 70)
        risk_level = "Low"
        if high_readings / len(blood_sugar_values) > 0.3 or low_readings / len(blood_sugar_values) > 0.2:
            risk_level = "High"
        elif high_readings / len(blood_sugar_values) > 0.2 or low_readings / len(blood_sugar_values) > 0.1:
            risk_level = "Moderate"
        
        # Compile patient analysis
        results["patient_analysis"][patient_id] = {
            "statistics": stats,
            "trend_analysis": {
                "direction": "increasing" if total_change > 0 else "decreasing",
                "percent_change": float(total_change),
                "moving_averages": [float(ma) for ma in moving_averages],
                "interpretation": "increasing" if total_change > 0 else "decreasing"
            },
            "anomalies": {
                "count": len(anomalies),
                "indices": anomaly_indices,
                "values": [float(v) for v in anomalies]
            },
            "pattern_analysis": {
                "patterns": patterns,
                "centers": pattern_centers,
                "stability_score": insights["pattern_analysis"]["stability_score"],
                "variability": insights["pattern_analysis"]["variability"]
            } if patterns else None,
            "risk_assessment": {
                "level": risk_level,
                "high_readings": high_readings,
                "low_readings": low_readings,
                "total_readings": len(blood_sugar_values)
            },
            "predictions": {
                "next_value": insights["prediction"]["predicted_value"],
                "confidence": insights["prediction"]["confidence"],
                "next_reading_time": insights["prediction"]["next_prediction_time"]
            },
            "recommendations": insights["recommendations"],
            "time_series": [{
                "timestamp": d["timestamp"].strftime("%Y-%m-%d %H:%M"),
                "value": float(d["blood_sugar"])
            } for d in patient_data]
        }
    
    # Overall insights
    all_values = [v for p in patients_data.values() for d in p if (v := d["blood_sugar"])]
    if all_values:
        results["overall_insights"] = {
            "total_patients": len(patients_data),
            "total_readings": len(all_values),
            "population_stats": {
                "average": float(round(statistics.mean(all_values), 2)),
                "std_dev": float(round(statistics.stdev(all_values), 2)) if len(all_values) > 1 else 0,
                "range": {
                    "min": float(min(all_values)),
                    "max": float(max(all_values))
                }
            },
            "risk_distribution": {
                "high_risk": sum(1 for p in results["patient_analysis"].values() if p["risk_assessment"]["level"] == "High"),
                "moderate_risk": sum(1 for p in results["patient_analysis"].values() if p["risk_assessment"]["level"] == "Moderate"),
                "low_risk": sum(1 for p in results["patient_analysis"].values() if p["risk_assessment"]["level"] == "Low")
            }
        }
    
    # Check if any analysis was performed
    if not results["analysis"]:
        # No analyzable columns were found, provide helpful information
        results["status"] = "warning"
        results["message"] = "No analyzable blood test metrics found in the uploaded file"
        results["available_columns"] = list(available_columns)
        results["expected_columns"] = metrics_to_analyze
        
        # Add a placeholder analysis to prevent frontend errors
        results["analysis"] = {
            "_info": {
                "message": "No analyzable blood test metrics found",
                "available_columns": list(available_columns),
                "expected_columns": metrics_to_analyze,
                "recommendation": "Please upload a file with standard blood test metrics or check column names"
            }
        }
    
    return results

def run_analysis(file_path: str, category: str) -> Dict[str, Any]:
    """Run analysis on the uploaded health data file."""
    print(f"Starting analysis of file: {file_path}, category: {category}")
    
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        print(error_msg)
        return {"error": error_msg}

    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
    data = None
    encoding_used = None
    last_error = None
    
    for encoding in encodings:
        try:
            print(f"Trying to read file with encoding: {encoding}")
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                if not content.strip():
                    print(f"File is empty with encoding {encoding}")
                    continue
                    
                try:
                    lines = content.splitlines()
                    if not lines:
                        print("No lines found in file")
                        continue
                        
                    reader = csv.DictReader(lines)
                    data = list(reader)
                    if data:
                        encoding_used = encoding
                        print(f"Successfully read file with encoding: {encoding}")
                        print(f"Found {len(data)} rows")
                        print(f"Columns: {list(data[0].keys())}")
                        break
                except csv.Error as csv_err:
                    print(f"CSV parsing error with encoding {encoding}: {str(csv_err)}")
                    last_error = csv_err
                    continue
                    
        except UnicodeDecodeError as ude:
            print(f"Unicode decode error with encoding {encoding}: {str(ude)}")
            last_error = ude
            continue
        except Exception as e:
            print(f"Error reading file with encoding {encoding}: {str(e)}")
            last_error = e
            continue
    
    if not data:
        error_msg = f"Could not read file with any supported encoding. Last error: {str(last_error)}"
        print(error_msg)
        return {
            "status": "error",
            "category": category,
            "error": error_msg
        }
    
    try:
        # Auto-detect category if not provided, set to auto, or if we can find a better match
        if not category or category == "unknown" or category == "auto":
            # Check for blood sugar related columns
            blood_sugar_columns = ['blood sugar', 'glucose', 'bloodsugar', 'sugar level', 'a1c']
            if "BloodSugar_mg_dL" in data[0] or any(any(col.lower() in field.lower() for col in blood_sugar_columns) for field in data[0].keys()):
                category = "blood_sugar"
                print(f"Auto-detected category: {category}")
            
            # Check for blood test related columns
            blood_test_columns = ['hemoglobin', 'white blood cells', 'red blood cells', 'platelets', 'hematocrit']
            if any(any(col.lower() in field.lower() for col in blood_test_columns) for field in data[0].keys()):
                category = "blood_test"
                print(f"Auto-detected category: {category}")
            
            # Check for vital signs related columns
            vital_signs_columns = ['heart rate', 'blood pressure', 'temperature', 'respiratory rate']
            if any(any(col.lower() in field.lower() for col in vital_signs_columns) for field in data[0].keys()):
                category = "vital_signs"
                print(f"Auto-detected category: {category}")
        
        # Check if this is a blood sugar report
        if "BloodSugar_mg_dL" in data[0] or category == "blood_sugar":
            print("Processing blood sugar report format")
            results = analyze_blood_sugar_data(data)
        # Initialize results based on category
        elif category == "blood_test":
            results = analyze_blood_test(data)
        elif category == "medical_history":
            results = analyze_medical_history(data)
        elif category == "vital_signs":
            results = analyze_vital_signs(data)
        else:
            # Provide more detailed generic analysis
            results = {
                "status": "success",
                "category": category or "unknown",
                "summary": {
                    "total_records": len(data),
                    "date_range": {
                        "start": data[0].get("Date") or data[0].get("Test Date") or "Unknown",
                        "end": data[-1].get("Date") or data[-1].get("Test Date") or "Unknown"
                    },
                    "message": "This file contains health data that requires further categorization. Please select a specific category for more detailed analysis."
                },
                "analysis": {
                    "columns": list(data[0].keys()),
                    "sample_values": {
                        col: [row[col] for row in data[:5] if col in row and row[col]]
                        for col in data[0].keys()
                    },
                    "possible_categories": ["blood_sugar", "blood_test", "vital_signs", "medical_history"]
                }
            }
        
        # Add file metadata
        results["file_metadata"] = {
            "encoding": encoding_used,
            "row_count": len(data),
            "columns": list(data[0].keys())
        }
        return results
            
    except Exception as e:
        error_msg = f"Error analyzing file: {str(e)}"
        print(error_msg)
        return {
            "status": "error",
            "category": category,
            "error": error_msg
        }

def get_date_range(data):
    """Extract date range from data if available"""
    date_columns = ['date', 'test date', 'collection date', 'sample date', 'timestamp', 'time']
    
    # Find a date column
    date_col = None
    for col in data[0].keys():
        if any(date_term.lower() in col.lower() for date_term in date_columns):
            date_col = col
            break
    
    if not date_col or not data:
        return {"start": None, "end": None}
    
    # Extract dates, handling potential missing values
    dates = [row.get(date_col) for row in data if row.get(date_col)]
    if not dates:
        return {"start": None, "end": None}
    
    return {"start": min(dates), "end": max(dates)}


def infer_data_category(data, columns):
    """Infer the data category based on the values in the data"""
    # Count occurrences of keywords in the data values
    keyword_counts = {
        "blood_sugar": 0,
        "blood_test": 0,
        "vital_signs": 0,
        "medical_history": 0
    }
    
    # Keywords for each category
    keywords = {
        "blood_sugar": ['glucose', 'sugar', 'a1c', 'hba1c', 'mg/dl', 'mmol/l', 'fasting', 'postprandial'],
        "blood_test": ['hemoglobin', 'wbc', 'rbc', 'platelets', 'cholesterol', 'triglycerides', 'hdl', 'ldl', 'creatinine'],
        "vital_signs": ['heart rate', 'blood pressure', 'temperature', 'bpm', 'systolic', 'diastolic', 'mmhg', 'celsius', 'fahrenheit'],
        "medical_history": ['diagnosis', 'condition', 'treatment', 'medication', 'allergies', 'surgery']
    }
    
    # Check column names first
    for col in columns:
        col_lower = col.lower()
        for category, terms in keywords.items():
            if any(term.lower() in col_lower for term in terms):
                keyword_counts[category] += 3  # Give more weight to column names
    
    # Check values in the first few rows
    sample_size = min(10, len(data))
    for row in data[:sample_size]:
        for col, value in row.items():
            if not value or not isinstance(value, str):
                continue
                
            value_lower = value.lower()
            for category, terms in keywords.items():
                if any(term.lower() in value_lower for term in terms):
                    keyword_counts[category] += 1
    
    # Check for numeric patterns in the data
    numeric_patterns = {
        "blood_sugar": r'\b([5-9][0-9]|1[0-9]{2}|2[0-9]{2}|3[0-9]{2}|4[0-9]{2})\s*(mg/dl|mg/dL)\b',  # 50-499 mg/dL
        "blood_pressure": r'\b(1[0-9]{2}|[6-9][0-9])/([4-9][0-9]|10[0-9])\b',  # 60-199/40-109
        "temperature": r'\b(3[5-9]\.[0-9]|4[0-1]\.[0-9])\s*[°C]\b|\b(9[5-9]\.[0-9]|10[0-9]\.[0-9])\s*[°F]\b'  # 35-41°C or 95-109°F
    }
    
    for row in data[:sample_size]:
        for col, value in row.items():
            if not value or not isinstance(value, str):
                continue
                
            if re.search(numeric_patterns["blood_sugar"], value):
                keyword_counts["blood_sugar"] += 2
            if re.search(numeric_patterns["blood_pressure"], value):
                keyword_counts["vital_signs"] += 2
            if re.search(numeric_patterns["temperature"], value):
                keyword_counts["vital_signs"] += 2
    
    # Find the category with the highest count
    max_count = 0
    inferred_category = None
    
    for category, count in keyword_counts.items():
        if count > max_count:
            max_count = count
            inferred_category = category
    
    # Only return a category if we have a reasonable confidence
    if max_count >= 3:
        return inferred_category
    
    return None


def analyze_blood_test(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze blood test data."""
    if not data:
        return {
            "status": "error",
            "category": "blood_test",
            "error": "No data provided for analysis",
            "analysis": {}
        }
        
    results = {
        "status": "success",
        "category": "blood_test",
        "analysis": {},
        "metadata": {
            "total_records": len(data),
            "date_range": {
                "start": data[0].get("Test Date") or data[0].get("Date") if data else None,
                "end": data[-1].get("Test Date") or data[-1].get("Date") if data else None
            },
            "notes": [row.get("Notes", "") for row in data if row.get("Notes")]
        }
    }
    
    # Define column mappings for different formats
    column_mappings = {
        # Standard blood test format
        "standard": [
            "Hemoglobin",
            "White Blood Cells",
            "Red Blood Cells",
            "Platelets",
            "Glucose"
        ],
        # Health data format
        "health_data": [
            "Blood Sugar Level (mg/dL)",
            "Blood Pressure (mmHg)",
            "Heart Rate (bpm)",
            "Temperature (°F)"  # Fixed degree symbol
        ]
    }
    
    # Determine which format we're dealing with
    available_columns = set()
    if data and len(data) > 0:
        available_columns = set(data[0].keys())
    format_type = "standard" if any(col in available_columns for col in column_mappings["standard"]) else "health_data"
    
    print(f"Detected format type: {format_type}")
    print(f"Available columns: {available_columns}")
    
    # Add format type to results
    results["format_type"] = format_type
    
    # Define metrics to analyze based on format
    metrics_to_analyze = column_mappings[format_type]
    
    # Log the metrics we're looking for
    print(f"Looking for metrics: {metrics_to_analyze}")
    
    for metric in metrics_to_analyze:
        # Handle encoding issues with degree symbol
        metric_in_file = metric
        if "°F" in metric:
            # Try different encodings of the degree symbol
            possible_metrics = [
                metric.replace("°", "°"),  # UTF-8
                metric.replace("°", "\u00b0"),  # Unicode escape
                metric.replace("°", "Â°"),  # Common misencoding
                metric.replace("°F", "F"),  # Without degree symbol
                metric.replace("°", "")  # Without degree symbol
            ]
            for possible_metric in possible_metrics:
                if possible_metric in data[0]:
                    metric_in_file = possible_metric
                    break
        
        if metric_in_file in data[0]:
            values = []
            timestamps = []
            for row in data:
                value = row[metric_in_file]
                timestamp = row.get("Test Date") or row.get("Date")
                
                if value and value.strip():
                    if "Blood Pressure" in metric_in_file:
                        try:
                            # Handle blood pressure format (e.g., "120/80")
                            systolic, diastolic = map(lambda x: float(x.strip()), value.split('/'))
                            values.append({"systolic": systolic, "diastolic": diastolic})
                            timestamps.append(timestamp)
                        except (ValueError, TypeError) as e:
                            print(f"Error parsing blood pressure value '{value}': {str(e)}")
                            continue
                    else:
                        try:
                            # Remove any units and special characters
                            clean_value = value.strip()
                            for unit in ["mg/dL", "bpm", "°F", "F", "g/dL", "cells/µL", "million/µL", "/µL"]:
                                clean_value = clean_value.replace(unit, "").strip()
                            # Remove any remaining parentheses and their contents
                            clean_value = re.sub(r'\([^)]*\)', '', clean_value).strip()
                            # Remove any commas in numbers
                            clean_value = clean_value.replace(',', '')
                            values.append(float(clean_value))
                            timestamps.append(timestamp)
                        except (ValueError, TypeError) as e:
                            print(f"Error parsing value '{value}' for metric '{metric_in_file}': {str(e)}")
                            continue
            
            if values:
                # Map the metric type for analysis
                metric_type = get_metric_type(metric)
                
                if metric_type == "blood pressure":
                    # Special handling for blood pressure
                    systolic_values = [v["systolic"] for v in values]
                    diastolic_values = [v["diastolic"] for v in values]
                    
                    results["analysis"][metric] = {
                        "systolic": analyze_health_metrics(systolic_values, "systolic blood pressure"),
                        "diastolic": analyze_health_metrics(diastolic_values, "diastolic blood pressure"),
                        "raw_values": values,
                        "timestamps": timestamps,
                        "trend_analysis": {
                            "systolic": analyze_trends(systolic_values),
                            "diastolic": analyze_trends(diastolic_values)
                        }
                    }
                else:
                    results["analysis"][metric] = analyze_health_metrics(values, metric_type)
                    results["analysis"][metric]["raw_values"] = values
                    results["analysis"][metric]["timestamps"] = timestamps
                    if len(values) > 1:
                        results["analysis"][metric]["trend_analysis"] = analyze_trends(values)
    
    return results

def get_metric_type(metric: str) -> str:
    """Map column names to metric types for analysis."""
    metric_lower = metric.lower()
    
    if "glucose" in metric_lower or "blood sugar" in metric_lower:
        return "blood sugar level"
    elif "pressure" in metric_lower:
        return "blood pressure"
    elif "heart rate" in metric_lower or "pulse" in metric_lower:
        return "heart rate"
    elif "temperature" in metric_lower:
        return "temperature"
    elif "hemoglobin" in metric_lower:
        return "hemoglobin"
    elif "white blood" in metric_lower:
        return "white blood cells"
    elif "red blood" in metric_lower:
        return "red blood cells"
    elif "platelets" in metric_lower:
        return "platelets"
    else:
        return "unknown"

def analyze_medical_history(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze medical history data."""
    return {
        "status": "success",
        "category": "medical_history",
        "summary": {
            "total_records": len(data),
            "date_range": {
                "start": data[0].get("Date") or data[0].get("Visit Date"),
                "end": data[-1].get("Date") or data[-1].get("Visit Date")
            }
        },
        "analysis": {
            "record_types": list(set(row.get("Record Type", "Unknown") for row in data)),
            "conditions": list(set(row.get("Condition", "Unknown") for row in data)),
            "treatments": list(set(row.get("Treatment", "Unknown") for row in data))
        }
    }

def analyze_vital_signs(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze vital signs data."""
    results = {
        "status": "success",
        "category": "vital_signs",
        "analysis": {}
    }
    
    metrics_to_analyze = [
        ("Blood Pressure", "blood pressure"),
        ("Heart Rate", "heart rate"),
        ("Temperature", "temperature"),
        ("Respiratory Rate", "respiratory rate"),
        ("Oxygen Saturation", "oxygen saturation")
    ]
    
    for column, metric_type in metrics_to_analyze:
        if column in data[0]:
            values = []
            for row in data:
                value = row[column]
                if value and value.strip():
                    if metric_type == "blood pressure":
                        values.append(value)  # Keep as string for blood pressure
                    else:
                        try:
                            values.append(float(value))
                        except ValueError:
                            continue
            
            if values:
                results["analysis"][column] = analyze_health_metrics(values, metric_type)
                # Add trend analysis
                if len(values) > 1:
                    results["analysis"][column]["trend_analysis"] = analyze_trends(values)
    
    return results
