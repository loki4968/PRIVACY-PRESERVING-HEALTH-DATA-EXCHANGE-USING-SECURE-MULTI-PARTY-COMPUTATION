"""
Oncology Analytics Service
Advanced cancer care analytics and treatment response analysis
"""

import math
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import csv
import os

class OncologyAnalytics:
    """
    Comprehensive oncology analytics including:
    - Treatment response analysis
    - Survival curve analysis (Kaplan-Meier)
    - Tumor marker trend analysis
    - Cancer staging and prognosis
    - Treatment effectiveness evaluation
    """
    
    def __init__(self):
        self.tumor_marker_ranges = {
            'psa': {
                'normal': (0, 4.0),
                'slightly_elevated': (4.0, 10.0),
                'moderately_elevated': (10.0, 20.0),
                'highly_elevated': (20.0, 100.0)
            },
            'cea': {
                'normal': (0, 3.0),
                'slightly_elevated': (3.0, 10.0),
                'moderately_elevated': (10.0, 20.0),
                'highly_elevated': (20.0, 100.0)
            },
            'ca125': {
                'normal': (0, 35.0),
                'slightly_elevated': (35.0, 100.0),
                'moderately_elevated': (100.0, 200.0),
                'highly_elevated': (200.0, 1000.0)
            },
            'ca199': {
                'normal': (0, 37.0),
                'slightly_elevated': (37.0, 100.0),
                'moderately_elevated': (100.0, 200.0),
                'highly_elevated': (200.0, 1000.0)
            },
            'afp': {
                'normal': (0, 10.0),
                'slightly_elevated': (10.0, 50.0),
                'moderately_elevated': (50.0, 200.0),
                'highly_elevated': (200.0, 1000.0)
            }
        }
        
        self.cancer_stages = {
            'T1N0M0': {'stage': 'I', 'prognosis': 'excellent', '5_year_survival': 95},
            'T2N0M0': {'stage': 'II', 'prognosis': 'very_good', '5_year_survival': 85},
            'T3N0M0': {'stage': 'III', 'prognosis': 'good', '5_year_survival': 70},
            'T1N1M0': {'stage': 'II', 'prognosis': 'good', '5_year_survival': 80},
            'T2N1M0': {'stage': 'III', 'prognosis': 'fair', '5_year_survival': 65},
            'T3N1M0': {'stage': 'III', 'prognosis': 'fair', '5_year_survival': 60},
            'T4N0M0': {'stage': 'IV', 'prognosis': 'guarded', '5_year_survival': 40},
            'T4N1M0': {'stage': 'IV', 'prognosis': 'guarded', '5_year_survival': 35},
            'T1N0M1': {'stage': 'IV', 'prognosis': 'poor', '5_year_survival': 25},
            'T2N0M1': {'stage': 'IV', 'prognosis': 'poor', '5_year_survival': 20},
            'T3N0M1': {'stage': 'IV', 'prognosis': 'poor', '5_year_survival': 15},
            'T4N1M1': {'stage': 'IV', 'prognosis': 'poor', '5_year_survival': 10},
            'T4N2M1': {'stage': 'IV', 'prognosis': 'very_poor', '5_year_survival': 5}
        }
        
        self.treatment_response_criteria = {
            'complete_response': 'Disappearance of all target lesions',
            'partial_response': '≥30% decrease in tumor markers',
            'stable_disease': '<30% decrease or <20% increase in tumor markers',
            'progressive_disease': '≥20% increase in tumor markers'
        }
    
    def treatment_response_analysis(self, patient_data: Dict, marker_history: List[Dict]) -> Dict:
        """
        Analyze treatment response based on tumor marker trends
        
        Args:
            patient_data: Patient information including cancer type and treatment
            marker_history: Historical tumor marker measurements
        
        Returns:
            Comprehensive treatment response analysis
        """
        if not marker_history:
            return {'error': 'No tumor marker history provided'}
        
        try:
            cancer_type = patient_data.get('cancer_type', 'unknown')
            treatment_start_date = patient_data.get('treatment_start_date', marker_history[0]['test_date'])
            
            # Identify primary tumor marker for this cancer type
            primary_marker = self._get_primary_marker(cancer_type)
            
            if not primary_marker:
                return {'error': f'No primary marker defined for cancer type: {cancer_type}'}
            
            # Extract marker values over time
            marker_values = []
            for reading in marker_history:
                if primary_marker in reading:
                    marker_values.append({
                        'date': reading['test_date'],
                        'value': reading[primary_marker],
                        'days_from_treatment': self._calculate_days_from_treatment(
                            reading['test_date'], treatment_start_date
                        )
                    })
            
            if len(marker_values) < 2:
                return {'error': 'Insufficient marker data for trend analysis'}
            
            # Calculate response metrics
            baseline_value = marker_values[0]['value']
            latest_value = marker_values[-1]['value']
            nadir_value = min(reading['value'] for reading in marker_values)
            peak_value = max(reading['value'] for reading in marker_values)
            
            # Calculate percentage change from baseline
            percent_change = ((latest_value - baseline_value) / baseline_value) * 100 if baseline_value > 0 else 0
            
            # Determine treatment response
            response_category = self._classify_treatment_response(percent_change)
            
            # Calculate trend analysis
            trend_analysis = self._analyze_marker_trend(marker_values)
            
            # Time to response/progression
            time_metrics = self._calculate_time_metrics(marker_values, baseline_value)
            
            return {
                'cancer_type': cancer_type,
                'primary_marker': primary_marker,
                'baseline_value': baseline_value,
                'latest_value': latest_value,
                'nadir_value': nadir_value,
                'peak_value': peak_value,
                'percent_change_from_baseline': round(percent_change, 1),
                'treatment_response': response_category,
                'trend_analysis': trend_analysis,
                'time_metrics': time_metrics,
                'clinical_interpretation': self._get_clinical_interpretation(response_category, trend_analysis),
                'monitoring_recommendations': self._get_monitoring_recommendations(response_category, cancer_type)
            }
            
        except Exception as e:
            return {'error': f"Treatment response analysis error: {str(e)}"}
    
    def _get_primary_marker(self, cancer_type: str) -> Optional[str]:
        """Get primary tumor marker for cancer type"""
        marker_mapping = {
            'prostate': 'psa_ng_ml',
            'colorectal': 'cea_ng_ml',
            'ovarian': 'ca125_u_ml',
            'pancreatic': 'ca199_u_ml',
            'liver': 'afp_ng_ml',
            'breast': 'ca125_u_ml'  # Can also use CEA
        }
        return marker_mapping.get(cancer_type.lower())
    
    def _calculate_days_from_treatment(self, test_date: str, treatment_start: str) -> int:
        """Calculate days from treatment start"""
        try:
            test_dt = datetime.strptime(test_date, '%Y-%m-%d')
            treatment_dt = datetime.strptime(treatment_start, '%Y-%m-%d')
            return (test_dt - treatment_dt).days
        except:
            return 0
    
    def _classify_treatment_response(self, percent_change: float) -> Dict:
        """Classify treatment response based on RECIST criteria"""
        if percent_change <= -30:
            return {
                'category': 'partial_response',
                'description': 'Partial Response (PR)',
                'clinical_significance': 'Treatment is effective'
            }
        elif percent_change <= -10:
            return {
                'category': 'minor_response',
                'description': 'Minor Response',
                'clinical_significance': 'Some treatment benefit'
            }
        elif percent_change <= 20:
            return {
                'category': 'stable_disease',
                'description': 'Stable Disease (SD)',
                'clinical_significance': 'Disease control achieved'
            }
        else:
            return {
                'category': 'progressive_disease',
                'description': 'Progressive Disease (PD)',
                'clinical_significance': 'Treatment not effective'
            }
    
    def _analyze_marker_trend(self, marker_values: List[Dict]) -> Dict:
        """Analyze tumor marker trend over time"""
        values = [reading['value'] for reading in marker_values]
        days = [reading['days_from_treatment'] for reading in marker_values]
        
        # Calculate trend slope (simple linear regression)
        if len(values) >= 2:
            n = len(values)
            sum_x = sum(days)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(days, values))
            sum_x2 = sum(x * x for x in days)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
            
            # Trend interpretation
            if slope < -0.1:
                trend_direction = 'decreasing'
                trend_interpretation = 'Favorable - marker decreasing'
            elif slope > 0.1:
                trend_direction = 'increasing'
                trend_interpretation = 'Concerning - marker increasing'
            else:
                trend_direction = 'stable'
                trend_interpretation = 'Stable - no significant change'
        else:
            slope = 0
            trend_direction = 'insufficient_data'
            trend_interpretation = 'Insufficient data for trend analysis'
        
        # Calculate velocity (rate of change)
        if len(values) >= 2:
            time_span = days[-1] - days[0] if days[-1] != days[0] else 1
            velocity = (values[-1] - values[0]) / time_span
        else:
            velocity = 0
        
        return {
            'slope': round(slope, 4),
            'trend_direction': trend_direction,
            'trend_interpretation': trend_interpretation,
            'velocity_per_day': round(velocity, 4),
            'data_points': len(values)
        }
    
    def _calculate_time_metrics(self, marker_values: List[Dict], baseline: float) -> Dict:
        """Calculate time-based treatment metrics"""
        metrics = {
            'time_to_nadir': None,
            'time_to_response': None,
            'time_to_progression': None,
            'duration_of_response': None
        }
        
        nadir_value = min(reading['value'] for reading in marker_values)
        nadir_index = next(i for i, reading in enumerate(marker_values) if reading['value'] == nadir_value)
        
        # Time to nadir (lowest point)
        metrics['time_to_nadir'] = marker_values[nadir_index]['days_from_treatment']
        
        # Time to response (30% decrease from baseline)
        response_threshold = baseline * 0.7
        for reading in marker_values:
            if reading['value'] <= response_threshold:
                metrics['time_to_response'] = reading['days_from_treatment']
                break
        
        # Time to progression (20% increase from nadir)
        progression_threshold = nadir_value * 1.2
        progression_day = None
        for reading in marker_values[nadir_index:]:
            if reading['value'] >= progression_threshold:
                progression_day = reading['days_from_treatment']
                break
        
        metrics['time_to_progression'] = progression_day
        
        # Duration of response
        if metrics['time_to_response'] and metrics['time_to_progression']:
            metrics['duration_of_response'] = metrics['time_to_progression'] - metrics['time_to_response']
        
        return metrics
    
    def _get_clinical_interpretation(self, response_category: Dict, trend_analysis: Dict) -> List[str]:
        """Generate clinical interpretation of treatment response"""
        interpretations = []
        
        category = response_category['category']
        trend = trend_analysis['trend_direction']
        
        if category == 'partial_response':
            interpretations.append("Excellent treatment response - continue current therapy")
            if trend == 'decreasing':
                interpretations.append("Continued improvement expected")
        elif category == 'minor_response':
            interpretations.append("Modest treatment benefit - monitor closely")
            if trend == 'stable':
                interpretations.append("Consider treatment optimization")
        elif category == 'stable_disease':
            interpretations.append("Disease stabilization achieved")
            if trend == 'increasing':
                interpretations.append("Watch for early signs of progression")
        else:  # progressive_disease
            interpretations.append("Treatment failure - consider alternative therapy")
            interpretations.append("Urgent oncology consultation recommended")
        
        return interpretations
    
    def _get_monitoring_recommendations(self, response_category: Dict, cancer_type: str) -> List[str]:
        """Get monitoring recommendations based on response"""
        recommendations = []
        
        category = response_category['category']
        
        if category == 'progressive_disease':
            recommendations.extend([
                "Increase monitoring frequency to every 2-4 weeks",
                "Consider imaging studies to assess disease extent",
                "Evaluate for alternative treatment options",
                "Assess performance status and quality of life"
            ])
        elif category == 'stable_disease':
            recommendations.extend([
                "Continue current monitoring schedule",
                "Monitor for early signs of progression",
                "Assess treatment tolerability"
            ])
        else:  # Response categories
            recommendations.extend([
                "Continue current treatment regimen",
                "Monitor for treatment-related toxicities",
                "Plan for long-term follow-up"
            ])
        
        # Cancer-specific recommendations
        if cancer_type.lower() == 'prostate':
            recommendations.append("Monitor for bone metastases with bone scan")
        elif cancer_type.lower() == 'colorectal':
            recommendations.append("Monitor liver function and CEA levels")
        elif cancer_type.lower() == 'ovarian':
            recommendations.append("Monitor for ascites and CA-125 trends")
        
        return recommendations
    
    def survival_analysis(self, patient_cohort: List[Dict]) -> Dict:
        """
        Perform survival analysis using Kaplan-Meier method
        
        Args:
            patient_cohort: List of patients with survival data
        
        Returns:
            Survival analysis results
        """
        if not patient_cohort:
            return {'error': 'No patient cohort data provided'}
        
        try:
            # Extract survival data
            survival_data = []
            for patient in patient_cohort:
                months_since_diagnosis = patient.get('months_since_diagnosis', 0)
                treatment_status = patient.get('treatment_status', 'unknown')
                cancer_stage = patient.get('stage', 'unknown')
                
                # Determine event status (1 = event occurred, 0 = censored)
                event_occurred = 1 if treatment_status in ['deceased', 'progression'] else 0
                
                survival_data.append({
                    'patient_id': patient.get('patient_id', 'unknown'),
                    'survival_time': months_since_diagnosis,
                    'event_occurred': event_occurred,
                    'cancer_stage': cancer_stage,
                    'treatment_status': treatment_status
                })
            
            # Sort by survival time
            survival_data.sort(key=lambda x: x['survival_time'])
            
            # Calculate Kaplan-Meier survival probabilities
            km_analysis = self._calculate_kaplan_meier(survival_data)
            
            # Survival statistics by stage
            stage_analysis = self._analyze_survival_by_stage(survival_data)
            
            # Median survival calculation
            median_survival = self._calculate_median_survival(km_analysis['survival_probabilities'])
            
            return {
                'total_patients': len(patient_cohort),
                'events_observed': sum(data['event_occurred'] for data in survival_data),
                'median_survival_months': median_survival,
                'kaplan_meier_analysis': km_analysis,
                'survival_by_stage': stage_analysis,
                'survival_rates': self._calculate_survival_rates(km_analysis['survival_probabilities']),
                'prognostic_factors': self._identify_prognostic_factors(survival_data)
            }
            
        except Exception as e:
            return {'error': f"Survival analysis error: {str(e)}"}
    
    def _calculate_kaplan_meier(self, survival_data: List[Dict]) -> Dict:
        """Calculate Kaplan-Meier survival probabilities"""
        # Group by survival time
        time_groups = {}
        for data in survival_data:
            time = data['survival_time']
            if time not in time_groups:
                time_groups[time] = {'at_risk': 0, 'events': 0}
            time_groups[time]['events'] += data['event_occurred']
        
        # Calculate number at risk for each time point
        total_patients = len(survival_data)
        cumulative_events = 0
        
        survival_probabilities = []
        cumulative_survival = 1.0
        
        for time in sorted(time_groups.keys()):
            at_risk = total_patients - cumulative_events
            events = time_groups[time]['events']
            
            if at_risk > 0:
                survival_probability = (at_risk - events) / at_risk
                cumulative_survival *= survival_probability
            
            survival_probabilities.append({
                'time_months': time,
                'at_risk': at_risk,
                'events': events,
                'survival_probability': round(cumulative_survival, 4)
            })
            
            cumulative_events += events
        
        return {
            'survival_probabilities': survival_probabilities,
            'total_follow_up_months': max(time_groups.keys()) if time_groups else 0
        }
    
    def _analyze_survival_by_stage(self, survival_data: List[Dict]) -> Dict:
        """Analyze survival by cancer stage"""
        stage_groups = {}
        
        for data in survival_data:
            stage = data['cancer_stage']
            if stage not in stage_groups:
                stage_groups[stage] = []
            stage_groups[stage].append(data)
        
        stage_analysis = {}
        for stage, patients in stage_groups.items():
            if patients:
                survival_times = [p['survival_time'] for p in patients]
                events = sum(p['event_occurred'] for p in patients)
                
                stage_analysis[stage] = {
                    'patient_count': len(patients),
                    'events': events,
                    'median_survival': statistics.median(survival_times),
                    'mean_survival': round(statistics.mean(survival_times), 1),
                    'event_rate': round((events / len(patients)) * 100, 1)
                }
        
        return stage_analysis
    
    def _calculate_median_survival(self, survival_probabilities: List[Dict]) -> Optional[float]:
        """Calculate median survival time"""
        for prob_data in survival_probabilities:
            if prob_data['survival_probability'] <= 0.5:
                return prob_data['time_months']
        return None  # Median not reached
    
    def _calculate_survival_rates(self, survival_probabilities: List[Dict]) -> Dict:
        """Calculate survival rates at key time points"""
        rates = {}
        key_timepoints = [6, 12, 24, 36, 60]  # months
        
        for timepoint in key_timepoints:
            # Find closest survival probability
            closest_prob = None
            for prob_data in survival_probabilities:
                if prob_data['time_months'] >= timepoint:
                    closest_prob = prob_data['survival_probability']
                    break
            
            if closest_prob is not None:
                rates[f'{timepoint}_month_survival'] = round(closest_prob * 100, 1)
        
        return rates
    
    def _identify_prognostic_factors(self, survival_data: List[Dict]) -> List[str]:
        """Identify key prognostic factors"""
        factors = []
        
        # Analyze stage distribution
        stages = [data['cancer_stage'] for data in survival_data]
        advanced_stages = sum(1 for stage in stages if any(advanced in stage for advanced in ['T3', 'T4', 'N1', 'N2', 'M1']))
        
        if advanced_stages / len(stages) > 0.5:
            factors.append("High proportion of advanced stage disease")
        
        # Analyze treatment status
        active_treatment = sum(1 for data in survival_data if data['treatment_status'] == 'active_treatment')
        if active_treatment / len(survival_data) > 0.7:
            factors.append("Majority of patients on active treatment")
        
        return factors
    
    def tumor_marker_trend_analysis(self, marker_data: List[Dict], marker_type: str) -> Dict:
        """
        Analyze tumor marker trends over time
        
        Args:
            marker_data: Historical marker measurements
            marker_type: Type of tumor marker (psa, cea, ca125, etc.)
        
        Returns:
            Comprehensive trend analysis
        """
        if not marker_data:
            return {'error': 'No marker data provided'}
        
        try:
            # Extract values and dates
            values = []
            dates = []
            
            for reading in marker_data:
                if marker_type in reading:
                    values.append(reading[marker_type])
                    dates.append(reading['test_date'])
            
            if len(values) < 2:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Basic statistics
            current_value = values[-1]
            baseline_value = values[0]
            min_value = min(values)
            max_value = max(values)
            
            # Trend calculations
            percent_change = ((current_value - baseline_value) / baseline_value) * 100 if baseline_value > 0 else 0
            
            # Doubling time calculation (for increasing markers)
            doubling_time = self._calculate_doubling_time(values, dates)
            
            # Marker velocity
            time_span_days = self._calculate_time_span(dates[0], dates[-1])
            velocity = (current_value - baseline_value) / time_span_days if time_span_days > 0 else 0
            
            # Clinical significance
            normal_range = self.tumor_marker_ranges.get(marker_type.replace('_ng_ml', '').replace('_u_ml', ''), {})
            clinical_status = self._assess_marker_clinical_status(current_value, normal_range)
            
            return {
                'marker_type': marker_type,
                'baseline_value': baseline_value,
                'current_value': current_value,
                'min_value': min_value,
                'max_value': max_value,
                'percent_change': round(percent_change, 1),
                'doubling_time_days': doubling_time,
                'velocity_per_day': round(velocity, 4),
                'clinical_status': clinical_status,
                'trend_interpretation': self._interpret_marker_trend(percent_change, doubling_time),
                'monitoring_recommendations': self._get_marker_monitoring_recommendations(clinical_status, percent_change)
            }
            
        except Exception as e:
            return {'error': f"Tumor marker trend analysis error: {str(e)}"}
    
    def _calculate_doubling_time(self, values: List[float], dates: List[str]) -> Optional[float]:
        """Calculate tumor marker doubling time"""
        if len(values) < 2 or values[0] <= 0:
            return None
        
        try:
            # Use exponential growth model: V(t) = V0 * e^(kt)
            # Doubling time = ln(2) / k
            
            baseline = values[0]
            current = values[-1]
            
            if current <= baseline:
                return None  # No growth
            
            time_span_days = self._calculate_time_span(dates[0], dates[-1])
            if time_span_days <= 0:
                return None
            
            # Calculate growth rate constant
            k = math.log(current / baseline) / time_span_days
            
            # Calculate doubling time
            doubling_time = math.log(2) / k if k > 0 else None
            
            return round(doubling_time, 1) if doubling_time else None
            
        except:
            return None
    
    def _calculate_time_span(self, start_date: str, end_date: str) -> int:
        """Calculate time span in days between two dates"""
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            return (end_dt - start_dt).days
        except:
            return 0
    
    def _assess_marker_clinical_status(self, value: float, normal_range: Dict) -> Dict:
        """Assess clinical status of tumor marker"""
        if not normal_range:
            return {'status': 'unknown', 'description': 'Normal range not defined'}
        
        for status, (min_val, max_val) in normal_range.items():
            if min_val <= value < max_val:
                return {
                    'status': status,
                    'description': status.replace('_', ' ').title(),
                    'value': value
                }
        
        return {'status': 'extremely_elevated', 'description': 'Extremely Elevated', 'value': value}
    
    def _interpret_marker_trend(self, percent_change: float, doubling_time: Optional[float]) -> str:
        """Interpret tumor marker trend"""
        if percent_change <= -50:
            return "Excellent response - significant marker decrease"
        elif percent_change <= -30:
            return "Good response - substantial marker decrease"
        elif percent_change <= -10:
            return "Modest response - minor marker decrease"
        elif percent_change <= 20:
            return "Stable disease - marker relatively unchanged"
        elif doubling_time and doubling_time < 90:
            return "Rapid progression - fast marker doubling time"
        elif percent_change > 50:
            return "Significant progression - major marker increase"
        else:
            return "Progression - marker increasing"
    
    def _get_marker_monitoring_recommendations(self, clinical_status: Dict, percent_change: float) -> List[str]:
        """Get monitoring recommendations based on marker status"""
        recommendations = []
        
        status = clinical_status['status']
        
        if status in ['highly_elevated', 'extremely_elevated']:
            recommendations.extend([
                "Frequent monitoring every 2-4 weeks",
                "Consider imaging studies",
                "Evaluate treatment response"
            ])
        elif status == 'moderately_elevated':
            recommendations.extend([
                "Monitor every 4-6 weeks",
                "Assess treatment effectiveness"
            ])
        else:
            recommendations.extend([
                "Standard monitoring every 8-12 weeks",
                "Continue current surveillance"
            ])
        
        if percent_change > 25:
            recommendations.append("Consider treatment modification")
        elif percent_change < -25:
            recommendations.append("Continue effective treatment")
        
        return recommendations
    
    def cancer_staging_analysis(self, patient_data: Dict) -> Dict:
        """
        Analyze cancer staging and provide prognosis
        
        Args:
            patient_data: Patient data including TNM staging
        
        Returns:
            Staging analysis and prognosis
        """
        try:
            tnm_stage = patient_data.get('stage', 'unknown')
            cancer_type = patient_data.get('cancer_type', 'unknown')
            age = patient_data.get('age', 0)
            
            # Get stage information
            stage_info = self.cancer_stages.get(tnm_stage, {
                'stage': 'unknown',
                'prognosis': 'unknown',
                '5_year_survival': 0
            })
            
            # Adjust prognosis based on age and other factors
            adjusted_prognosis = self._adjust_prognosis_for_age(stage_info, age)
            
            # Generate recommendations
            recommendations = self._get_staging_recommendations(stage_info, cancer_type)
            
            return {
                'tnm_staging': tnm_stage,
                'overall_stage': stage_info['stage'],
                'prognosis': stage_info['prognosis'],
                'five_year_survival_rate': stage_info['5_year_survival'],
                'age_adjusted_prognosis': adjusted_prognosis,
                'treatment_recommendations': recommendations,
                'follow_up_schedule': self._get_follow_up_schedule(stage_info['stage'], cancer_type)
            }
            
        except Exception as e:
            return {'error': f"Cancer staging analysis error: {str(e)}"}
    
    def _adjust_prognosis_for_age(self, stage_info: Dict, age: int) -> Dict:
        """Adjust prognosis based on patient age"""
        base_survival = stage_info['5_year_survival']
        
        # Age adjustment factors
        if age < 50:
            adjustment_factor = 1.1  # Better prognosis for younger patients
        elif age < 65:
            adjustment_factor = 1.0  # Standard prognosis
        elif age < 75:
            adjustment_factor = 0.9  # Slightly worse prognosis
        else:
            adjustment_factor = 0.8  # Worse prognosis for elderly
        
        adjusted_survival = min(base_survival * adjustment_factor, 100)
        
        return {
            'age_group': 'young' if age < 50 else 'middle_aged' if age < 65 else 'elderly' if age < 75 else 'very_elderly',
            'adjustment_factor': adjustment_factor,
            'age_adjusted_survival': round(adjusted_survival, 1)
        }
    
    def _get_staging_recommendations(self, stage_info: Dict, cancer_type: str) -> List[str]:
        """Get treatment recommendations based on staging"""
        stage = stage_info['stage']
        recommendations = []
        
        if stage == 'I':
            recommendations.extend([
                "Surgical resection if operable",
                "Consider adjuvant therapy based on risk factors",
                "Regular surveillance"
            ])
        elif stage == 'II':
            recommendations.extend([
                "Surgical resection with lymph node evaluation",
                "Adjuvant therapy recommended",
                "Close monitoring for recurrence"
            ])
        elif stage == 'III':
            recommendations.extend([
                "Multimodal therapy approach",
                "Neoadjuvant therapy consideration",
                "Surgical resection if feasible",
                "Adjuvant chemotherapy/radiation"
            ])
        else:  # Stage IV
            recommendations.extend([
                "Palliative care consultation",
                "Systemic therapy (chemotherapy/immunotherapy)",
                "Symptom management",
                "Quality of life focus"
            ])
        
        # Cancer-specific recommendations
        if cancer_type.lower() == 'prostate':
            recommendations.append("Consider hormone therapy")
        elif cancer_type.lower() == 'breast':
            recommendations.append("Hormone receptor testing")
        elif cancer_type.lower() == 'lung':
            recommendations.append("Molecular profiling for targeted therapy")
        
        return recommendations
    
    def _get_follow_up_schedule(self, stage: str, cancer_type: str) -> Dict:
        """Get follow-up schedule based on cancer stage"""
        if stage in ['I', 'II']:
            return {
                'clinic_visits': 'Every 3-6 months for 2 years, then annually',
                'imaging': 'Every 6-12 months',
                'tumor_markers': 'Every 3-6 months if applicable',
                'duration': '5-10 years'
            }
        elif stage == 'III':
            return {
                'clinic_visits': 'Every 3 months for 2 years, then every 6 months',
                'imaging': 'Every 3-6 months',
                'tumor_markers': 'Every 3 months if applicable',
                'duration': 'Lifelong'
            }
        else:  # Stage IV
            return {
                'clinic_visits': 'Every 4-8 weeks',
                'imaging': 'Every 2-3 months',
                'tumor_markers': 'Every 4-8 weeks if applicable',
                'duration': 'Ongoing'
            }

# Example usage and testing functions
def test_oncology_analytics():
    """Test the oncology analytics functions"""
    oncology_analytics = OncologyAnalytics()
    
    # Test tumor marker data
    test_marker_data = [
        {'test_date': '2024-01-01', 'psa_ng_ml': 8.5, 'cea_ng_ml': 2.1, 'ca125_u_ml': 25.0},
        {'test_date': '2024-02-01', 'psa_ng_ml': 12.3, 'cea_ng_ml': 3.2, 'ca125_u_ml': 28.0},
        {'test_date': '2024-03-01', 'psa_ng_ml': 15.8, 'cea_ng_ml': 4.1, 'ca125_u_ml': 32.0},
        {'test_date': '2024-04-01', 'psa_ng_ml': 18.2, 'cea_ng_ml': 5.5, 'ca125_u_ml': 38.0}
    ]
    
    # Test patient data
    test_patient = {
        'cancer_type': 'prostate',
        'treatment_start_date': '2024-01-15',
        'stage': 'T2N0M0',
        'age': 65
    }
    
    # Test treatment response analysis
    print("🔬 Testing Treatment Response Analysis:")
    response_result = oncology_analytics.treatment_response_analysis(test_patient, test_marker_data)
    print(f"Treatment Response: {response_result}")
    
    # Test tumor marker trend analysis
    print("\n📈 Testing Tumor Marker Trend Analysis:")
    trend_result = oncology_analytics.tumor_marker_trend_analysis(test_marker_data, 'psa_ng_ml')
    print(f"Marker Trend: {trend_result}")
    
    # Test cancer staging analysis
    print("\n🎯 Testing Cancer Staging Analysis:")
    staging_result = oncology_analytics.cancer_staging_analysis(test_patient)
    print(f"Cancer Staging: {staging_result}")
    
    # Test survival analysis with sample cohort
    test_cohort = [
        {'patient_id': 'P001', 'months_since_diagnosis': 24, 'treatment_status': 'active_treatment', 'stage': 'T1N0M0'},
        {'patient_id': 'P002', 'months_since_diagnosis': 18, 'treatment_status': 'deceased', 'stage': 'T3N1M0'},
        {'patient_id': 'P003', 'months_since_diagnosis': 36, 'treatment_status': 'active_treatment', 'stage': 'T2N0M0'},
        {'patient_id': 'P004', 'months_since_diagnosis': 12, 'treatment_status': 'progression', 'stage': 'T4N1M1'},
        {'patient_id': 'P005', 'months_since_diagnosis': 48, 'treatment_status': 'remission', 'stage': 'T1N0M0'}
    ]
    
    print("\n📊 Testing Survival Analysis:")
    survival_result = oncology_analytics.survival_analysis(test_cohort)
    print(f"Survival Analysis: {survival_result}")
    
    return oncology_analytics

if __name__ == "__main__":
    test_oncology_analytics()
