"""
Cardiovascular Analytics Service
Advanced cardiovascular risk assessment and analysis algorithms
"""

import math
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import csv
import os

class CardiovascularAnalytics:
    """
    Comprehensive cardiovascular analytics including:
    - Framingham Risk Score calculation
    - Hypertension classification (AHA guidelines)
    - Cardiac biomarker analysis
    - Blood pressure trend analysis
    - Cholesterol risk stratification
    """
    
    def __init__(self):
        self.aha_bp_categories = {
            'normal': {'systolic': (0, 120), 'diastolic': (0, 80)},
            'elevated': {'systolic': (120, 130), 'diastolic': (0, 80)},
            'stage1_hypertension': {'systolic': (130, 140), 'diastolic': (80, 90)},
            'stage2_hypertension': {'systolic': (140, 180), 'diastolic': (90, 120)},
            'hypertensive_crisis': {'systolic': (180, 300), 'diastolic': (120, 200)}
        }
        
        self.cholesterol_ranges = {
            'total_cholesterol': {
                'desirable': (0, 200),
                'borderline_high': (200, 240),
                'high': (240, 500)
            },
            'ldl_cholesterol': {
                'optimal': (0, 100),
                'near_optimal': (100, 130),
                'borderline_high': (130, 160),
                'high': (160, 190),
                'very_high': (190, 500)
            },
            'hdl_cholesterol': {
                'low': (0, 40),  # for men; <50 for women
                'normal': (40, 60),
                'high': (60, 150)
            }
        }
    
    def framingham_risk_score(self, patient_data: Dict) -> Dict:
        """
        Calculate 10-year cardiovascular risk using Framingham Risk Score
        
        Args:
            patient_data: Dictionary containing patient information
                - age: int
                - gender: str ('M' or 'F')
                - total_cholesterol: float (mg/dL)
                - hdl_cholesterol: float (mg/dL)
                - systolic_bp: float (mmHg)
                - smoking_status: str ('current', 'former', 'never')
                - diabetes_status: str ('yes' or 'no')
                - hypertension_treatment: bool
        
        Returns:
            Dictionary with risk score and interpretation
        """
        try:
            age = patient_data.get('age', 0)
            gender = patient_data.get('gender', 'M').upper()
            total_chol = patient_data.get('total_cholesterol', 200)
            hdl_chol = patient_data.get('hdl_cholesterol', 50)
            systolic_bp = patient_data.get('systolic_bp', 120)
            smoking = patient_data.get('smoking_status', 'never')
            diabetes = patient_data.get('diabetes_status', 'no')
            bp_treatment = patient_data.get('hypertension_treatment', False)
            
            # Age points
            if gender == 'M':
                if age < 35: age_points = -9
                elif age < 40: age_points = -4
                elif age < 45: age_points = 0
                elif age < 50: age_points = 3
                elif age < 55: age_points = 6
                elif age < 60: age_points = 8
                elif age < 65: age_points = 10
                elif age < 70: age_points = 11
                elif age < 75: age_points = 12
                else: age_points = 13
            else:  # Female
                if age < 35: age_points = -7
                elif age < 40: age_points = -3
                elif age < 45: age_points = 0
                elif age < 50: age_points = 3
                elif age < 55: age_points = 6
                elif age < 60: age_points = 8
                elif age < 65: age_points = 10
                elif age < 70: age_points = 12
                elif age < 75: age_points = 14
                else: age_points = 16
            
            # Total cholesterol points
            if gender == 'M':
                if total_chol < 160: chol_points = 0
                elif total_chol < 200: chol_points = 4
                elif total_chol < 240: chol_points = 7
                elif total_chol < 280: chol_points = 9
                else: chol_points = 11
            else:  # Female
                if total_chol < 160: chol_points = 0
                elif total_chol < 200: chol_points = 4
                elif total_chol < 240: chol_points = 8
                elif total_chol < 280: chol_points = 11
                else: chol_points = 13
            
            # HDL cholesterol points
            if hdl_chol >= 60: hdl_points = -1
            elif hdl_chol >= 50: hdl_points = 0
            elif hdl_chol >= 40: hdl_points = 1
            else: hdl_points = 2
            
            # Blood pressure points
            if bp_treatment:
                if systolic_bp < 120: bp_points = 0
                elif systolic_bp < 130: bp_points = 1
                elif systolic_bp < 140: bp_points = 2
                elif systolic_bp < 160: bp_points = 3
                else: bp_points = 4
            else:
                if systolic_bp < 120: bp_points = 0
                elif systolic_bp < 130: bp_points = 0
                elif systolic_bp < 140: bp_points = 1
                elif systolic_bp < 160: bp_points = 1
                else: bp_points = 2
            
            # Smoking points
            smoking_points = 8 if smoking == 'current' else 0
            
            # Diabetes points
            diabetes_points = 6 if diabetes.lower() == 'yes' else 0
            
            # Calculate total points
            total_points = (age_points + chol_points + hdl_points + 
                          bp_points + smoking_points + diabetes_points)
            
            # Convert to 10-year risk percentage
            if gender == 'M':
                risk_lookup = {
                    0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3,
                    8: 4, 9: 5, 10: 6, 11: 8, 12: 10, 13: 12, 14: 16,
                    15: 20, 16: 25, 17: 30
                }
            else:  # Female
                risk_lookup = {
                    9: 1, 10: 1, 11: 1, 12: 1, 13: 2, 14: 2, 15: 3,
                    16: 4, 17: 5, 18: 6, 19: 8, 20: 11, 21: 14, 22: 17,
                    23: 22, 24: 27, 25: 30
                }
            
            risk_percentage = risk_lookup.get(total_points, 30 if total_points > max(risk_lookup.keys()) else 1)
            
            # Risk interpretation
            if risk_percentage < 7.5:
                risk_category = "Low Risk"
                recommendations = ["Continue healthy lifestyle", "Regular monitoring"]
            elif risk_percentage < 20:
                risk_category = "Intermediate Risk"
                recommendations = ["Consider statin therapy", "Lifestyle modifications", "More frequent monitoring"]
            else:
                risk_category = "High Risk"
                recommendations = ["Statin therapy recommended", "Aggressive lifestyle changes", "Frequent medical follow-up"]
            
            return {
                'framingham_score': total_points,
                'ten_year_risk_percentage': risk_percentage,
                'risk_category': risk_category,
                'recommendations': recommendations,
                'component_scores': {
                    'age_points': age_points,
                    'cholesterol_points': chol_points,
                    'hdl_points': hdl_points,
                    'blood_pressure_points': bp_points,
                    'smoking_points': smoking_points,
                    'diabetes_points': diabetes_points
                }
            }
            
        except Exception as e:
            return {'error': f"Framingham calculation error: {str(e)}"}
    
    def classify_hypertension(self, bp_readings: List[Dict]) -> Dict:
        """
        Classify hypertension stage based on AHA guidelines
        
        Args:
            bp_readings: List of blood pressure readings with 'systolic_bp' and 'diastolic_bp'
        
        Returns:
            Dictionary with classification and analysis
        """
        if not bp_readings:
            return {'error': 'No blood pressure readings provided'}
        
        try:
            # Calculate average BP
            systolic_values = [reading['systolic_bp'] for reading in bp_readings]
            diastolic_values = [reading['diastolic_bp'] for reading in bp_readings]
            
            avg_systolic = statistics.mean(systolic_values)
            avg_diastolic = statistics.mean(diastolic_values)
            
            # Classify based on AHA guidelines
            classification = self._classify_single_bp(avg_systolic, avg_diastolic)
            
            # Additional analysis
            elevated_readings = sum(1 for reading in bp_readings 
                                  if self._classify_single_bp(reading['systolic_bp'], reading['diastolic_bp'])['category'] 
                                  in ['elevated', 'stage1_hypertension', 'stage2_hypertension', 'hypertensive_crisis'])
            
            bp_variability = {
                'systolic_std': statistics.stdev(systolic_values) if len(systolic_values) > 1 else 0,
                'diastolic_std': statistics.stdev(diastolic_values) if len(diastolic_values) > 1 else 0
            }
            
            return {
                'average_bp': {'systolic': round(avg_systolic, 1), 'diastolic': round(avg_diastolic, 1)},
                'classification': classification,
                'total_readings': len(bp_readings),
                'elevated_readings': elevated_readings,
                'elevated_percentage': round((elevated_readings / len(bp_readings)) * 100, 1),
                'bp_variability': bp_variability,
                'recommendations': self._get_bp_recommendations(classification['category'])
            }
            
        except Exception as e:
            return {'error': f"Hypertension classification error: {str(e)}"}
    
    def _classify_single_bp(self, systolic: float, diastolic: float) -> Dict:
        """Classify a single blood pressure reading"""
        # Hypertensive crisis (emergency)
        if systolic >= 180 or diastolic >= 120:
            return {
                'category': 'hypertensive_crisis',
                'description': 'Hypertensive Crisis',
                'severity': 'emergency'
            }
        
        # Stage 2 Hypertension
        elif systolic >= 140 or diastolic >= 90:
            return {
                'category': 'stage2_hypertension',
                'description': 'Stage 2 Hypertension',
                'severity': 'high'
            }
        
        # Stage 1 Hypertension
        elif systolic >= 130 or diastolic >= 80:
            return {
                'category': 'stage1_hypertension',
                'description': 'Stage 1 Hypertension',
                'severity': 'moderate'
            }
        
        # Elevated
        elif systolic >= 120 and diastolic < 80:
            return {
                'category': 'elevated',
                'description': 'Elevated Blood Pressure',
                'severity': 'mild'
            }
        
        # Normal
        else:
            return {
                'category': 'normal',
                'description': 'Normal Blood Pressure',
                'severity': 'none'
            }
    
    def _get_bp_recommendations(self, category: str) -> List[str]:
        """Get recommendations based on BP category"""
        recommendations = {
            'normal': [
                "Maintain healthy lifestyle",
                "Regular exercise",
                "Balanced diet",
                "Annual BP checks"
            ],
            'elevated': [
                "Lifestyle modifications",
                "Reduce sodium intake",
                "Increase physical activity",
                "Weight management",
                "Recheck in 3-6 months"
            ],
            'stage1_hypertension': [
                "Lifestyle changes plus medication consideration",
                "DASH diet implementation",
                "Regular exercise program",
                "Stress management",
                "Monthly monitoring"
            ],
            'stage2_hypertension': [
                "Medication therapy required",
                "Comprehensive lifestyle changes",
                "Weekly monitoring initially",
                "Specialist consultation",
                "Cardiovascular risk assessment"
            ],
            'hypertensive_crisis': [
                "IMMEDIATE MEDICAL ATTENTION",
                "Emergency department evaluation",
                "Continuous monitoring",
                "Immediate medication adjustment"
            ]
        }
        
        return recommendations.get(category, ["Consult healthcare provider"])
    
    def analyze_cholesterol_profile(self, cholesterol_data: Dict) -> Dict:
        """
        Comprehensive cholesterol profile analysis
        
        Args:
            cholesterol_data: Dictionary with cholesterol values
        
        Returns:
            Detailed cholesterol analysis and recommendations
        """
        try:
            total_chol = cholesterol_data.get('total_cholesterol', 0)
            ldl_chol = cholesterol_data.get('ldl_cholesterol', 0)
            hdl_chol = cholesterol_data.get('hdl_cholesterol', 0)
            triglycerides = cholesterol_data.get('triglycerides', 0)
            gender = cholesterol_data.get('gender', 'M')
            
            # Classify each component
            total_chol_class = self._classify_cholesterol_component(total_chol, 'total_cholesterol')
            ldl_chol_class = self._classify_cholesterol_component(ldl_chol, 'ldl_cholesterol')
            hdl_chol_class = self._classify_cholesterol_component(hdl_chol, 'hdl_cholesterol', gender)
            triglycerides_class = self._classify_triglycerides(triglycerides)
            
            # Calculate ratios
            total_hdl_ratio = total_chol / hdl_chol if hdl_chol > 0 else 0
            ldl_hdl_ratio = ldl_chol / hdl_chol if hdl_chol > 0 else 0
            
            # Overall risk assessment
            risk_factors = []
            if total_chol_class['risk_level'] in ['borderline_high', 'high']:
                risk_factors.append('High total cholesterol')
            if ldl_chol_class['risk_level'] in ['high', 'very_high']:
                risk_factors.append('High LDL cholesterol')
            if hdl_chol_class['risk_level'] == 'low':
                risk_factors.append('Low HDL cholesterol')
            if triglycerides_class['risk_level'] in ['borderline_high', 'high', 'very_high']:
                risk_factors.append('High triglycerides')
            
            overall_risk = 'high' if len(risk_factors) >= 2 else 'moderate' if risk_factors else 'low'
            
            return {
                'total_cholesterol': total_chol_class,
                'ldl_cholesterol': ldl_chol_class,
                'hdl_cholesterol': hdl_chol_class,
                'triglycerides': triglycerides_class,
                'ratios': {
                    'total_hdl_ratio': round(total_hdl_ratio, 2),
                    'ldl_hdl_ratio': round(ldl_hdl_ratio, 2)
                },
                'overall_risk': overall_risk,
                'risk_factors': risk_factors,
                'recommendations': self._get_cholesterol_recommendations(overall_risk, risk_factors)
            }
            
        except Exception as e:
            return {'error': f"Cholesterol analysis error: {str(e)}"}
    
    def _classify_cholesterol_component(self, value: float, component: str, gender: str = 'M') -> Dict:
        """Classify individual cholesterol components"""
        ranges = self.cholesterol_ranges.get(component, {})
        
        if component == 'hdl_cholesterol':
            # Adjust HDL ranges for gender
            low_threshold = 50 if gender.upper() == 'F' else 40
            if value < low_threshold:
                return {'value': value, 'classification': 'Low', 'risk_level': 'low'}
            elif value < 60:
                return {'value': value, 'classification': 'Normal', 'risk_level': 'normal'}
            else:
                return {'value': value, 'classification': 'High (Protective)', 'risk_level': 'high'}
        
        # For total and LDL cholesterol
        for classification, (min_val, max_val) in ranges.items():
            if min_val <= value < max_val:
                return {
                    'value': value,
                    'classification': classification.replace('_', ' ').title(),
                    'risk_level': classification
                }
        
        return {'value': value, 'classification': 'Unknown', 'risk_level': 'unknown'}
    
    def _classify_triglycerides(self, value: float) -> Dict:
        """Classify triglyceride levels"""
        if value < 150:
            return {'value': value, 'classification': 'Normal', 'risk_level': 'normal'}
        elif value < 200:
            return {'value': value, 'classification': 'Borderline High', 'risk_level': 'borderline_high'}
        elif value < 500:
            return {'value': value, 'classification': 'High', 'risk_level': 'high'}
        else:
            return {'value': value, 'classification': 'Very High', 'risk_level': 'very_high'}
    
    def _get_cholesterol_recommendations(self, overall_risk: str, risk_factors: List[str]) -> List[str]:
        """Generate cholesterol management recommendations"""
        base_recommendations = [
            "Heart-healthy diet (Mediterranean or DASH)",
            "Regular physical activity (150 min/week)",
            "Maintain healthy weight",
            "Avoid tobacco use"
        ]
        
        if overall_risk == 'high':
            base_recommendations.extend([
                "Consider statin therapy",
                "Frequent lipid monitoring",
                "Cardiovascular risk assessment",
                "Specialist consultation recommended"
            ])
        elif overall_risk == 'moderate':
            base_recommendations.extend([
                "Enhanced lifestyle modifications",
                "Consider medication if lifestyle changes insufficient",
                "Monitor lipids every 6 months"
            ])
        else:
            base_recommendations.append("Annual lipid screening")
        
        return base_recommendations
    
    def cardiac_event_prediction(self, patient_history: Dict) -> Dict:
        """
        Predict cardiac event risk based on comprehensive patient data
        
        Args:
            patient_history: Comprehensive patient data including biomarkers, history, etc.
        
        Returns:
            Risk prediction and recommendations
        """
        try:
            # Calculate Framingham risk
            framingham_result = self.framingham_risk_score(patient_history)
            
            # Additional risk factors
            additional_risk_score = 0
            risk_modifiers = []
            
            # Family history
            if patient_history.get('family_history_cvd', False):
                additional_risk_score += 2
                risk_modifiers.append('Family history of CVD')
            
            # CRP levels (if available)
            crp = patient_history.get('crp_mg_l', 0)
            if crp > 3.0:
                additional_risk_score += 2
                risk_modifiers.append('Elevated CRP (inflammation)')
            
            # Metabolic syndrome components
            metabolic_components = 0
            if patient_history.get('waist_circumference', 0) > (102 if patient_history.get('gender') == 'M' else 88):
                metabolic_components += 1
            if patient_history.get('triglycerides', 0) >= 150:
                metabolic_components += 1
            if patient_history.get('hdl_cholesterol', 50) < (40 if patient_history.get('gender') == 'M' else 50):
                metabolic_components += 1
            if patient_history.get('systolic_bp', 120) >= 130 or patient_history.get('diastolic_bp', 80) >= 85:
                metabolic_components += 1
            if patient_history.get('fasting_glucose', 90) >= 100:
                metabolic_components += 1
            
            if metabolic_components >= 3:
                additional_risk_score += 3
                risk_modifiers.append('Metabolic syndrome')
            
            # Adjust base risk
            base_risk = framingham_result.get('ten_year_risk_percentage', 5)
            adjusted_risk = min(base_risk + additional_risk_score, 50)  # Cap at 50%
            
            # Final risk category
            if adjusted_risk < 5:
                final_risk_category = "Very Low Risk"
            elif adjusted_risk < 7.5:
                final_risk_category = "Low Risk"
            elif adjusted_risk < 20:
                final_risk_category = "Intermediate Risk"
            else:
                final_risk_category = "High Risk"
            
            return {
                'framingham_risk': framingham_result,
                'additional_risk_factors': risk_modifiers,
                'adjusted_risk_percentage': adjusted_risk,
                'final_risk_category': final_risk_category,
                'recommendations': self._get_cardiac_prevention_recommendations(final_risk_category),
                'monitoring_frequency': self._get_monitoring_frequency(final_risk_category)
            }
            
        except Exception as e:
            return {'error': f"Cardiac prediction error: {str(e)}"}
    
    def _get_cardiac_prevention_recommendations(self, risk_category: str) -> List[str]:
        """Get cardiac prevention recommendations based on risk"""
        base_recommendations = [
            "Heart-healthy diet",
            "Regular exercise",
            "Smoking cessation if applicable",
            "Stress management"
        ]
        
        if risk_category == "High Risk":
            base_recommendations.extend([
                "Statin therapy strongly recommended",
                "Consider aspirin therapy",
                "Aggressive blood pressure control",
                "Diabetes management if applicable",
                "Cardiology consultation"
            ])
        elif risk_category == "Intermediate Risk":
            base_recommendations.extend([
                "Consider statin therapy",
                "Enhanced lifestyle modifications",
                "Regular cardiovascular monitoring"
            ])
        
        return base_recommendations
    
    def _get_monitoring_frequency(self, risk_category: str) -> Dict:
        """Get recommended monitoring frequency"""
        if risk_category == "High Risk":
            return {
                'lipid_panel': 'Every 3 months',
                'blood_pressure': 'Weekly',
                'comprehensive_exam': 'Every 6 months'
            }
        elif risk_category == "Intermediate Risk":
            return {
                'lipid_panel': 'Every 6 months',
                'blood_pressure': 'Monthly',
                'comprehensive_exam': 'Annually'
            }
        else:
            return {
                'lipid_panel': 'Annually',
                'blood_pressure': 'Every 6 months',
                'comprehensive_exam': 'Every 2 years'
            }

# Example usage and testing functions
def test_cardiovascular_analytics():
    """Test the cardiovascular analytics functions"""
    cv_analytics = CardiovascularAnalytics()
    
    # Test patient data
    test_patient = {
        'age': 55,
        'gender': 'M',
        'total_cholesterol': 240,
        'hdl_cholesterol': 35,
        'systolic_bp': 145,
        'smoking_status': 'current',
        'diabetes_status': 'no',
        'hypertension_treatment': True
    }
    
    # Test Framingham Risk Score
    print("🔬 Testing Framingham Risk Score:")
    framingham_result = cv_analytics.framingham_risk_score(test_patient)
    print(f"Risk Score: {framingham_result}")
    
    # Test BP readings
    bp_readings = [
        {'systolic_bp': 145, 'diastolic_bp': 92},
        {'systolic_bp': 142, 'diastolic_bp': 88},
        {'systolic_bp': 148, 'diastolic_bp': 94}
    ]
    
    print("\n🩺 Testing Hypertension Classification:")
    bp_result = cv_analytics.classify_hypertension(bp_readings)
    print(f"BP Classification: {bp_result}")
    
    return cv_analytics

if __name__ == "__main__":
    test_cardiovascular_analytics()
