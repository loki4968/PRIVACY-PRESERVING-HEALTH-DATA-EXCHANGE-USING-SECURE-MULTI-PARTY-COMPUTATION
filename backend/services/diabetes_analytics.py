"""
Diabetes Analytics Service
Advanced diabetes management and glycemic control analysis
"""

import math
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import csv
import os

class DiabetesAnalytics:
    """
    Comprehensive diabetes analytics including:
    - Glycemic control assessment
    - Insulin optimization recommendations
    - Diabetic complication risk analysis
    - Time-in-range calculations
    - HbA1c prediction and trends
    """
    
    def __init__(self):
        self.glucose_ranges = {
            'hypoglycemic_severe': (0, 54),      # <54 mg/dL
            'hypoglycemic_mild': (54, 70),       # 54-69 mg/dL
            'target_range': (70, 180),           # 70-180 mg/dL (standard)
            'hyperglycemic_mild': (180, 250),    # 180-250 mg/dL
            'hyperglycemic_severe': (250, 600)   # >250 mg/dL
        }
        
        self.hba1c_targets = {
            'excellent': (0, 6.5),
            'good': (6.5, 7.0),
            'fair': (7.0, 8.0),
            'poor': (8.0, 9.0),
            'very_poor': (9.0, 15.0)
        }
        
        self.diabetes_complications_risk_factors = {
            'retinopathy': ['duration_years', 'hba1c_avg', 'blood_pressure'],
            'nephropathy': ['duration_years', 'hba1c_avg', 'blood_pressure', 'protein_urine'],
            'neuropathy': ['duration_years', 'hba1c_avg', 'age'],
            'cardiovascular': ['hba1c_avg', 'cholesterol', 'blood_pressure', 'smoking']
        }
    
    def glycemic_control_assessment(self, glucose_data: List[Dict]) -> Dict:
        """
        Comprehensive glycemic control evaluation
        
        Args:
            glucose_data: List of glucose readings with timestamps and values
        
        Returns:
            Detailed glycemic control analysis
        """
        if not glucose_data:
            return {'error': 'No glucose data provided'}
        
        try:
            glucose_values = [reading['glucose_level'] for reading in glucose_data]
            
            # Basic statistics
            avg_glucose = statistics.mean(glucose_values)
            glucose_std = statistics.stdev(glucose_values) if len(glucose_values) > 1 else 0
            min_glucose = min(glucose_values)
            max_glucose = max(glucose_values)
            
            # Time in Range (TIR) calculations
            tir_analysis = self._calculate_time_in_range(glucose_values)
            
            # Glycemic variability
            cv = (glucose_std / avg_glucose) * 100 if avg_glucose > 0 else 0
            
            # Estimated HbA1c (using formula: eA1C = (avg_glucose + 46.7) / 28.7)
            estimated_hba1c = (avg_glucose + 46.7) / 28.7
            
            # Risk episodes
            hypoglycemic_episodes = self._count_hypoglycemic_episodes(glucose_data)
            hyperglycemic_episodes = self._count_hyperglycemic_episodes(glucose_data)
            
            # Overall control assessment
            control_quality = self._assess_glycemic_control_quality(
                avg_glucose, cv, tir_analysis['target_range_percentage'], 
                hypoglycemic_episodes['total'], hyperglycemic_episodes['total']
            )
            
            return {
                'basic_statistics': {
                    'average_glucose': round(avg_glucose, 1),
                    'glucose_std': round(glucose_std, 1),
                    'min_glucose': min_glucose,
                    'max_glucose': max_glucose,
                    'coefficient_of_variation': round(cv, 1),
                    'total_readings': len(glucose_values)
                },
                'time_in_range': tir_analysis,
                'estimated_hba1c': round(estimated_hba1c, 1),
                'hypoglycemic_episodes': hypoglycemic_episodes,
                'hyperglycemic_episodes': hyperglycemic_episodes,
                'glycemic_control_quality': control_quality,
                'recommendations': self._get_glycemic_control_recommendations(control_quality, tir_analysis, cv)
            }
            
        except Exception as e:
            return {'error': f"Glycemic control assessment error: {str(e)}"}
    
    def _calculate_time_in_range(self, glucose_values: List[float]) -> Dict:
        """Calculate time in range percentages"""
        total_readings = len(glucose_values)
        
        ranges = {
            'very_low': sum(1 for g in glucose_values if g < 54),
            'low': sum(1 for g in glucose_values if 54 <= g < 70),
            'target_range': sum(1 for g in glucose_values if 70 <= g <= 180),
            'high': sum(1 for g in glucose_values if 180 < g <= 250),
            'very_high': sum(1 for g in glucose_values if g > 250)
        }
        
        percentages = {
            f"{range_name}_percentage": round((count / total_readings) * 100, 1)
            for range_name, count in ranges.items()
        }
        
        # Clinical targets
        target_achievement = {
            'tir_target_met': percentages['target_range_percentage'] >= 70,  # >70% in range
            'hypoglycemia_acceptable': (percentages['very_low_percentage'] + percentages['low_percentage']) < 4,  # <4% low
            'hyperglycemia_acceptable': (percentages['high_percentage'] + percentages['very_high_percentage']) < 25  # <25% high
        }
        
        return {**ranges, **percentages, **target_achievement}
    
    def _count_hypoglycemic_episodes(self, glucose_data: List[Dict]) -> Dict:
        """Count and analyze hypoglycemic episodes"""
        episodes = {'mild': 0, 'severe': 0, 'total': 0, 'longest_duration': 0}
        
        current_episode_duration = 0
        in_hypoglycemic_episode = False
        
        for reading in glucose_data:
            glucose = reading['glucose_level']
            
            if glucose < 70:  # Hypoglycemic threshold
                if not in_hypoglycemic_episode:
                    episodes['total'] += 1
                    if glucose < 54:
                        episodes['severe'] += 1
                    else:
                        episodes['mild'] += 1
                    in_hypoglycemic_episode = True
                    current_episode_duration = 1
                else:
                    current_episode_duration += 1
            else:
                if in_hypoglycemic_episode:
                    episodes['longest_duration'] = max(episodes['longest_duration'], current_episode_duration)
                    in_hypoglycemic_episode = False
                    current_episode_duration = 0
        
        return episodes
    
    def _count_hyperglycemic_episodes(self, glucose_data: List[Dict]) -> Dict:
        """Count and analyze hyperglycemic episodes"""
        episodes = {'mild': 0, 'severe': 0, 'total': 0, 'longest_duration': 0}
        
        current_episode_duration = 0
        in_hyperglycemic_episode = False
        
        for reading in glucose_data:
            glucose = reading['glucose_level']
            
            if glucose > 180:  # Hyperglycemic threshold
                if not in_hyperglycemic_episode:
                    episodes['total'] += 1
                    if glucose > 250:
                        episodes['severe'] += 1
                    else:
                        episodes['mild'] += 1
                    in_hyperglycemic_episode = True
                    current_episode_duration = 1
                else:
                    current_episode_duration += 1
            else:
                if in_hyperglycemic_episode:
                    episodes['longest_duration'] = max(episodes['longest_duration'], current_episode_duration)
                    in_hyperglycemic_episode = False
                    current_episode_duration = 0
        
        return episodes
    
    def _assess_glycemic_control_quality(self, avg_glucose: float, cv: float, 
                                       tir_percentage: float, hypo_episodes: int, 
                                       hyper_episodes: int) -> Dict:
        """Assess overall glycemic control quality"""
        score = 0
        factors = []
        
        # Average glucose score (target: 70-180 mg/dL)
        if 70 <= avg_glucose <= 180:
            score += 25
            factors.append("Good average glucose")
        elif 180 < avg_glucose <= 200:
            score += 15
            factors.append("Slightly elevated average glucose")
        elif avg_glucose > 200:
            score += 5
            factors.append("High average glucose")
        else:
            score += 10
            factors.append("Low average glucose")
        
        # Glycemic variability (CV target: <36%)
        if cv < 36:
            score += 25
            factors.append("Good glycemic stability")
        else:
            score += 10
            factors.append("High glycemic variability")
        
        # Time in range (target: >70%)
        if tir_percentage >= 70:
            score += 25
            factors.append("Excellent time in range")
        elif tir_percentage >= 50:
            score += 15
            factors.append("Good time in range")
        else:
            score += 5
            factors.append("Poor time in range")
        
        # Hypoglycemic episodes (fewer is better)
        if hypo_episodes == 0:
            score += 15
            factors.append("No hypoglycemic episodes")
        elif hypo_episodes <= 2:
            score += 10
            factors.append("Few hypoglycemic episodes")
        else:
            score += 0
            factors.append("Frequent hypoglycemic episodes")
        
        # Hyperglycemic episodes (fewer is better)
        if hyper_episodes <= 5:
            score += 10
            factors.append("Few hyperglycemic episodes")
        else:
            score += 0
            factors.append("Frequent hyperglycemic episodes")
        
        # Overall quality assessment
        if score >= 80:
            quality = "Excellent"
        elif score >= 60:
            quality = "Good"
        elif score >= 40:
            quality = "Fair"
        else:
            quality = "Poor"
        
        return {
            'overall_score': score,
            'quality_rating': quality,
            'contributing_factors': factors
        }
    
    def insulin_optimization(self, patient_data: Dict, glucose_history: List[Dict]) -> Dict:
        """
        Insulin optimization recommendations based on glucose patterns
        
        Args:
            patient_data: Patient information including current insulin regimen
            glucose_history: Historical glucose readings with meal context
        
        Returns:
            Insulin optimization recommendations
        """
        try:
            current_regimen = patient_data.get('insulin_regimen', {})
            diabetes_type = patient_data.get('diabetes_type', 'type2')
            weight = patient_data.get('weight_kg', 70)
            
            # Analyze glucose patterns by meal context
            patterns = self._analyze_glucose_patterns(glucose_history)
            
            # Calculate total daily insulin needs (if Type 1)
            if diabetes_type.lower() == 'type1':
                total_daily_insulin = self._calculate_total_daily_insulin(weight, patterns['average_glucose'])
                basal_insulin = total_daily_insulin * 0.5  # 50% basal
                bolus_insulin = total_daily_insulin * 0.5  # 50% bolus
            else:
                # Type 2 - start with conservative dosing
                total_daily_insulin = weight * 0.3  # 0.3 units/kg starting dose
                basal_insulin = total_daily_insulin * 0.6  # 60% basal for Type 2
                bolus_insulin = total_daily_insulin * 0.4  # 40% bolus
            
            # Adjustment recommendations based on patterns
            adjustments = self._generate_insulin_adjustments(patterns, current_regimen)
            
            return {
                'current_analysis': patterns,
                'recommended_total_daily_insulin': round(total_daily_insulin, 1),
                'recommended_basal_insulin': round(basal_insulin, 1),
                'recommended_bolus_insulin': round(bolus_insulin, 1),
                'specific_adjustments': adjustments,
                'monitoring_recommendations': self._get_insulin_monitoring_recommendations(),
                'safety_considerations': self._get_insulin_safety_considerations()
            }
            
        except Exception as e:
            return {'error': f"Insulin optimization error: {str(e)}"}
    
    def _analyze_glucose_patterns(self, glucose_history: List[Dict]) -> Dict:
        """Analyze glucose patterns by meal context and time"""
        patterns = {
            'fasting': [],
            'pre_meal': [],
            'postprandial': [],
            'bedtime': [],
            'overall': []
        }
        
        for reading in glucose_history:
            glucose = reading['glucose_level']
            context = reading.get('measurement_type', 'unknown').lower()
            
            patterns['overall'].append(glucose)
            
            if 'fasting' in context:
                patterns['fasting'].append(glucose)
            elif 'pre' in context or 'before' in context:
                patterns['pre_meal'].append(glucose)
            elif 'post' in context or 'after' in context:
                patterns['postprandial'].append(glucose)
            elif 'bedtime' in context:
                patterns['bedtime'].append(glucose)
        
        # Calculate averages for each pattern
        pattern_analysis = {}
        for pattern_type, values in patterns.items():
            if values:
                pattern_analysis[f'{pattern_type}_average'] = round(statistics.mean(values), 1)
                pattern_analysis[f'{pattern_type}_count'] = len(values)
                pattern_analysis[f'{pattern_type}_std'] = round(statistics.stdev(values) if len(values) > 1 else 0, 1)
            else:
                pattern_analysis[f'{pattern_type}_average'] = 0
                pattern_analysis[f'{pattern_type}_count'] = 0
                pattern_analysis[f'{pattern_type}_std'] = 0
        
        return pattern_analysis
    
    def _calculate_total_daily_insulin(self, weight_kg: float, avg_glucose: float) -> float:
        """Calculate total daily insulin needs"""
        # Base calculation: 0.5-1.0 units/kg for Type 1
        base_insulin = weight_kg * 0.7  # Start with 0.7 units/kg
        
        # Adjust based on glucose control
        if avg_glucose > 200:
            adjustment_factor = 1.3
        elif avg_glucose > 150:
            adjustment_factor = 1.1
        elif avg_glucose < 100:
            adjustment_factor = 0.8
        else:
            adjustment_factor = 1.0
        
        return base_insulin * adjustment_factor
    
    def _generate_insulin_adjustments(self, patterns: Dict, current_regimen: Dict) -> List[Dict]:
        """Generate specific insulin adjustment recommendations"""
        adjustments = []
        
        # Fasting glucose adjustments (basal insulin)
        fasting_avg = patterns.get('fasting_average', 0)
        if fasting_avg > 130:
            adjustments.append({
                'type': 'basal_increase',
                'recommendation': 'Increase basal insulin by 10-20%',
                'reason': f'Fasting glucose elevated at {fasting_avg} mg/dL',
                'target': 'Fasting glucose 80-130 mg/dL'
            })
        elif fasting_avg < 70:
            adjustments.append({
                'type': 'basal_decrease',
                'recommendation': 'Decrease basal insulin by 10-15%',
                'reason': f'Fasting glucose low at {fasting_avg} mg/dL',
                'target': 'Prevent hypoglycemia'
            })
        
        # Postprandial adjustments (bolus insulin)
        postprandial_avg = patterns.get('postprandial_average', 0)
        if postprandial_avg > 180:
            adjustments.append({
                'type': 'bolus_increase',
                'recommendation': 'Increase meal bolus insulin by 10-15%',
                'reason': f'Post-meal glucose elevated at {postprandial_avg} mg/dL',
                'target': 'Post-meal glucose <180 mg/dL'
            })
        
        # Pre-meal adjustments
        pre_meal_avg = patterns.get('pre_meal_average', 0)
        if pre_meal_avg > 130:
            adjustments.append({
                'type': 'correction_bolus',
                'recommendation': 'Consider correction bolus before meals',
                'reason': f'Pre-meal glucose elevated at {pre_meal_avg} mg/dL',
                'target': 'Pre-meal glucose 80-130 mg/dL'
            })
        
        return adjustments
    
    def _get_insulin_monitoring_recommendations(self) -> List[str]:
        """Get insulin monitoring recommendations"""
        return [
            "Monitor blood glucose 4-6 times daily during adjustment period",
            "Check fasting glucose daily",
            "Monitor post-meal glucose 2 hours after eating",
            "Keep detailed log of insulin doses and glucose readings",
            "Watch for signs of hypoglycemia",
            "Adjust insulin doses gradually (10-20% changes)",
            "Consult healthcare provider before major changes"
        ]
    
    def _get_insulin_safety_considerations(self) -> List[str]:
        """Get insulin safety considerations"""
        return [
            "Never skip meals after taking rapid-acting insulin",
            "Always have glucose tablets or quick-acting carbs available",
            "Rotate injection sites to prevent lipodystrophy",
            "Store insulin properly (refrigerate unopened, room temp when in use)",
            "Check expiration dates regularly",
            "Inform family/friends about hypoglycemia symptoms and treatment",
            "Wear medical identification",
            "Adjust insulin for exercise and illness"
        ]
    
    def diabetic_complication_risk_analysis(self, patient_profile: Dict) -> Dict:
        """
        Assess risk for diabetic complications
        
        Args:
            patient_profile: Comprehensive patient data
        
        Returns:
            Risk analysis for major diabetic complications
        """
        try:
            duration_years = patient_profile.get('diagnosis_years', 0)
            hba1c_latest = patient_profile.get('hba1c_latest', 7.0)
            age = patient_profile.get('age', 50)
            systolic_bp = patient_profile.get('systolic_bp', 120)
            total_cholesterol = patient_profile.get('total_cholesterol', 200)
            smoking_status = patient_profile.get('smoking_status', 'never')
            
            complications_risk = {}
            
            # Diabetic Retinopathy Risk
            retinopathy_risk = self._calculate_retinopathy_risk(
                duration_years, hba1c_latest, systolic_bp
            )
            complications_risk['retinopathy'] = retinopathy_risk
            
            # Diabetic Nephropathy Risk
            nephropathy_risk = self._calculate_nephropathy_risk(
                duration_years, hba1c_latest, systolic_bp
            )
            complications_risk['nephropathy'] = nephropathy_risk
            
            # Diabetic Neuropathy Risk
            neuropathy_risk = self._calculate_neuropathy_risk(
                duration_years, hba1c_latest, age
            )
            complications_risk['neuropathy'] = neuropathy_risk
            
            # Cardiovascular Disease Risk
            cvd_risk = self._calculate_diabetes_cvd_risk(
                hba1c_latest, total_cholesterol, systolic_bp, smoking_status, age
            )
            complications_risk['cardiovascular'] = cvd_risk
            
            # Overall risk summary
            high_risk_complications = [comp for comp, risk in complications_risk.items() 
                                     if risk['risk_level'] == 'high']
            
            overall_assessment = {
                'high_risk_complications': high_risk_complications,
                'total_complications_assessed': len(complications_risk),
                'requires_immediate_attention': len(high_risk_complications) > 0,
                'prevention_priority': 'high' if high_risk_complications else 'moderate'
            }
            
            return {
                'individual_risks': complications_risk,
                'overall_assessment': overall_assessment,
                'prevention_recommendations': self._get_complication_prevention_recommendations(complications_risk),
                'screening_schedule': self._get_screening_schedule(complications_risk)
            }
            
        except Exception as e:
            return {'error': f"Complication risk analysis error: {str(e)}"}
    
    def _calculate_retinopathy_risk(self, duration: int, hba1c: float, bp: int) -> Dict:
        """Calculate diabetic retinopathy risk"""
        risk_score = 0
        
        # Duration factor
        if duration >= 15:
            risk_score += 3
        elif duration >= 10:
            risk_score += 2
        elif duration >= 5:
            risk_score += 1
        
        # HbA1c factor
        if hba1c >= 9.0:
            risk_score += 3
        elif hba1c >= 8.0:
            risk_score += 2
        elif hba1c >= 7.0:
            risk_score += 1
        
        # Blood pressure factor
        if bp >= 140:
            risk_score += 2
        elif bp >= 130:
            risk_score += 1
        
        # Risk level
        if risk_score >= 6:
            risk_level = 'high'
        elif risk_score >= 3:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': [
                f"Diabetes duration: {duration} years",
                f"HbA1c: {hba1c}%",
                f"Blood pressure: {bp} mmHg"
            ],
            'screening_frequency': 'annually' if risk_level == 'high' else 'every 2 years'
        }
    
    def _calculate_nephropathy_risk(self, duration: int, hba1c: float, bp: int) -> Dict:
        """Calculate diabetic nephropathy risk"""
        risk_score = 0
        
        # Duration factor (stronger for nephropathy)
        if duration >= 20:
            risk_score += 4
        elif duration >= 15:
            risk_score += 3
        elif duration >= 10:
            risk_score += 2
        elif duration >= 5:
            risk_score += 1
        
        # HbA1c factor
        if hba1c >= 9.0:
            risk_score += 3
        elif hba1c >= 8.0:
            risk_score += 2
        elif hba1c >= 7.0:
            risk_score += 1
        
        # Hypertension is major risk factor for nephropathy
        if bp >= 140:
            risk_score += 3
        elif bp >= 130:
            risk_score += 2
        
        # Risk level
        if risk_score >= 7:
            risk_level = 'high'
        elif risk_score >= 4:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': [
                f"Diabetes duration: {duration} years",
                f"HbA1c: {hba1c}%",
                f"Blood pressure: {bp} mmHg"
            ],
            'screening_frequency': 'every 6 months' if risk_level == 'high' else 'annually'
        }
    
    def _calculate_neuropathy_risk(self, duration: int, hba1c: float, age: int) -> Dict:
        """Calculate diabetic neuropathy risk"""
        risk_score = 0
        
        # Duration factor
        if duration >= 15:
            risk_score += 3
        elif duration >= 10:
            risk_score += 2
        elif duration >= 5:
            risk_score += 1
        
        # HbA1c factor
        if hba1c >= 9.0:
            risk_score += 3
        elif hba1c >= 8.0:
            risk_score += 2
        elif hba1c >= 7.0:
            risk_score += 1
        
        # Age factor (neuropathy increases with age)
        if age >= 65:
            risk_score += 2
        elif age >= 55:
            risk_score += 1
        
        # Risk level
        if risk_score >= 6:
            risk_level = 'high'
        elif risk_score >= 3:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': [
                f"Diabetes duration: {duration} years",
                f"HbA1c: {hba1c}%",
                f"Age: {age} years"
            ],
            'screening_frequency': 'annually'
        }
    
    def _calculate_diabetes_cvd_risk(self, hba1c: float, cholesterol: float, 
                                   bp: int, smoking: str, age: int) -> Dict:
        """Calculate cardiovascular disease risk in diabetes"""
        risk_score = 0
        
        # Diabetes itself is a major CVD risk factor
        risk_score += 2
        
        # HbA1c factor
        if hba1c >= 9.0:
            risk_score += 3
        elif hba1c >= 8.0:
            risk_score += 2
        elif hba1c >= 7.0:
            risk_score += 1
        
        # Cholesterol factor
        if cholesterol >= 240:
            risk_score += 3
        elif cholesterol >= 200:
            risk_score += 2
        
        # Blood pressure factor
        if bp >= 140:
            risk_score += 3
        elif bp >= 130:
            risk_score += 2
        
        # Smoking factor
        if smoking == 'current':
            risk_score += 3
        elif smoking == 'former':
            risk_score += 1
        
        # Age factor
        if age >= 65:
            risk_score += 2
        elif age >= 55:
            risk_score += 1
        
        # Risk level
        if risk_score >= 10:
            risk_level = 'high'
        elif risk_score >= 6:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': [
                f"HbA1c: {hba1c}%",
                f"Total cholesterol: {cholesterol} mg/dL",
                f"Blood pressure: {bp} mmHg",
                f"Smoking status: {smoking}",
                f"Age: {age} years"
            ],
            'prevention_priority': 'high' if risk_level == 'high' else 'moderate'
        }
    
    def _get_complication_prevention_recommendations(self, complications_risk: Dict) -> Dict:
        """Generate prevention recommendations based on risk analysis"""
        recommendations = {
            'general': [
                "Maintain HbA1c <7% (or individualized target)",
                "Control blood pressure <130/80 mmHg",
                "Manage cholesterol levels",
                "Quit smoking if applicable",
                "Regular physical activity",
                "Healthy diet and weight management"
            ],
            'specific': {}
        }
        
        for complication, risk_data in complications_risk.items():
            if risk_data['risk_level'] == 'high':
                if complication == 'retinopathy':
                    recommendations['specific']['retinopathy'] = [
                        "Immediate ophthalmologic evaluation",
                        "Strict glycemic control",
                        "Blood pressure optimization",
                        "Annual dilated eye exams"
                    ]
                elif complication == 'nephropathy':
                    recommendations['specific']['nephropathy'] = [
                        "ACE inhibitor or ARB therapy",
                        "Protein restriction if indicated",
                        "Regular kidney function monitoring",
                        "Avoid nephrotoxic medications"
                    ]
                elif complication == 'neuropathy':
                    recommendations['specific']['neuropathy'] = [
                        "Daily foot inspection",
                        "Proper foot care and footwear",
                        "Pain management if symptomatic",
                        "Regular neurological assessment"
                    ]
                elif complication == 'cardiovascular':
                    recommendations['specific']['cardiovascular'] = [
                        "Statin therapy",
                        "Aspirin therapy consideration",
                        "Aggressive blood pressure control",
                        "Cardiac risk stratification"
                    ]
        
        return recommendations
    
    def _get_screening_schedule(self, complications_risk: Dict) -> Dict:
        """Generate screening schedule based on risk levels"""
        schedule = {}
        
        for complication, risk_data in complications_risk.items():
            if complication == 'retinopathy':
                if risk_data['risk_level'] == 'high':
                    schedule['eye_exam'] = 'Every 6 months'
                else:
                    schedule['eye_exam'] = 'Annually'
            
            elif complication == 'nephropathy':
                if risk_data['risk_level'] == 'high':
                    schedule['kidney_function'] = 'Every 3 months'
                else:
                    schedule['kidney_function'] = 'Every 6 months'
            
            elif complication == 'neuropathy':
                schedule['foot_exam'] = 'Every visit (at least annually)'
                schedule['neurological_assessment'] = 'Annually'
            
            elif complication == 'cardiovascular':
                if risk_data['risk_level'] == 'high':
                    schedule['lipid_panel'] = 'Every 3 months'
                    schedule['cardiac_assessment'] = 'Every 6 months'
                else:
                    schedule['lipid_panel'] = 'Every 6 months'
                    schedule['cardiac_assessment'] = 'Annually'
        
        return schedule
    
    def _get_glycemic_control_recommendations(self, control_quality: Dict, 
                                           tir_analysis: Dict, cv: float) -> List[str]:
        """Generate glycemic control recommendations"""
        recommendations = []
        
        quality = control_quality['quality_rating']
        
        if quality == 'Poor':
            recommendations.extend([
                "Urgent diabetes management review needed",
                "Consider intensive insulin therapy",
                "Frequent glucose monitoring (6-8 times daily)",
                "Diabetes education reinforcement",
                "Endocrinologist consultation recommended"
            ])
        elif quality == 'Fair':
            recommendations.extend([
                "Medication adjustment needed",
                "Increase glucose monitoring frequency",
                "Review carbohydrate counting",
                "Consider continuous glucose monitoring"
            ])
        elif quality == 'Good':
            recommendations.extend([
                "Continue current management",
                "Fine-tune insulin doses",
                "Maintain regular monitoring"
            ])
        else:  # Excellent
            recommendations.extend([
                "Excellent control - maintain current regimen",
                "Continue regular monitoring",
                "Focus on long-term complications prevention"
            ])
        
        # Specific recommendations based on TIR
        if tir_analysis['target_range_percentage'] < 50:
            recommendations.append("Focus on improving time in range (currently <50%)")
        
        # Variability recommendations
        if cv > 36:
            recommendations.append("Work on reducing glucose variability")
            recommendations.append("Consider continuous glucose monitoring")
        
        return recommendations

# Example usage and testing functions
def test_diabetes_analytics():
    """Test the diabetes analytics functions"""
    diabetes_analytics = DiabetesAnalytics()
    
    # Test glucose data
    test_glucose_data = [
        {'glucose_level': 145, 'measurement_type': 'fasting', 'timestamp': '2024-01-15 07:00:00'},
        {'glucose_level': 185, 'measurement_type': 'postprandial', 'timestamp': '2024-01-15 09:30:00'},
        {'glucose_level': 98, 'measurement_type': 'pre_meal', 'timestamp': '2024-01-15 12:00:00'},
        {'glucose_level': 220, 'measurement_type': 'postprandial', 'timestamp': '2024-01-15 14:30:00'},
        {'glucose_level': 156, 'measurement_type': 'pre_meal', 'timestamp': '2024-01-15 18:00:00'},
        {'glucose_level': 195, 'measurement_type': 'postprandial', 'timestamp': '2024-01-15 20:30:00'},
        {'glucose_level': 128, 'measurement_type': 'bedtime', 'timestamp': '2024-01-15 22:00:00'}
    ]
    
    # Test glycemic control assessment
    print("🔬 Testing Glycemic Control Assessment:")
    glycemic_result = diabetes_analytics.glycemic_control_assessment(test_glucose_data)
    print(f"Glycemic Control: {glycemic_result}")
    
    # Test patient data for complications risk
    test_patient = {
        'diagnosis_years': 8,
        'hba1c_latest': 7.8,
        'age': 55,
        'systolic_bp': 145,
        'total_cholesterol': 220,
        'smoking_status': 'former'
    }
    
    print("\n🩺 Testing Diabetic Complications Risk:")
    complications_result = diabetes_analytics.diabetic_complication_risk_analysis(test_patient)
    print(f"Complications Risk: {complications_result}")
    
    return diabetes_analytics

if __name__ == "__main__":
    test_diabetes_analytics()
