#!/usr/bin/env python3
"""
Health Data Exchange - Multi-Condition Dataset Overview
Comprehensive analysis and validation of medical datasets
"""

import pandas as pd
import os
import json
from datetime import datetime
import numpy as np

class MedicalDatasetAnalyzer:
    def __init__(self, datasets_dir="datasets"):
        self.datasets_dir = datasets_dir
        self.analysis_results = {}
        
    def analyze_all_datasets(self):
        """Analyze all medical condition datasets"""
        print("🏥 Health Data Exchange - Multi-Condition Dataset Analysis")
        print("=" * 60)
        
        # Define dataset categories and files
        dataset_categories = {
            "cardiovascular": [
                "blood_pressure_readings.csv",
                "cholesterol_panels.csv"
            ],
            "diabetes": [
                "glucose_monitoring.csv"
            ],
            "oncology": [
                "tumor_markers.csv"
            ],
            "mental_health": [
                "depression_anxiety_scores.csv"
            ],
            "laboratory": [
                "complete_blood_count.csv"
            ],
            "vital_signs": [
                "comprehensive_vitals.csv"
            ]
        }
        
        total_records = 0
        total_patients = set()
        
        for category, files in dataset_categories.items():
            print(f"\n📊 {category.upper()} DATASETS:")
            print("-" * 40)
            
            category_records = 0
            category_patients = set()
            
            for filename in files:
                filepath = os.path.join(self.datasets_dir, category, filename)
                if os.path.exists(filepath):
                    df = pd.read_csv(filepath)
                    records = len(df)
                    
                    # Extract patient IDs
                    if 'patient_id' in df.columns:
                        patients = set(df['patient_id'].unique())
                        category_patients.update(patients)
                        total_patients.update(patients)
                    
                    category_records += records
                    total_records += records
                    
                    print(f"  ✅ {filename}")
                    print(f"     Records: {records}")
                    print(f"     Columns: {len(df.columns)}")
                    print(f"     Date Range: {self._get_date_range(df)}")
                    print(f"     Key Metrics: {self._get_key_metrics(df, category)}")
                    
                    # Store analysis results
                    self.analysis_results[f"{category}_{filename}"] = {
                        "records": records,
                        "columns": len(df.columns),
                        "patients": len(patients) if 'patient_id' in df.columns else 0,
                        "date_range": self._get_date_range(df),
                        "key_metrics": self._get_key_metrics(df, category)
                    }
                else:
                    print(f"  ❌ {filename} - File not found")
            
            print(f"  📈 Category Summary:")
            print(f"     Total Records: {category_records}")
            print(f"     Unique Patients: {len(category_patients)}")
        
        # Overall summary
        print(f"\n🎯 OVERALL DATASET SUMMARY:")
        print("=" * 40)
        print(f"Total Records: {total_records}")
        print(f"Unique Patients: {len(total_patients)}")
        print(f"Medical Conditions: {len(dataset_categories)}")
        print(f"Dataset Files: {sum(len(files) for files in dataset_categories.values())}")
        
        return self.analysis_results
    
    def _get_date_range(self, df):
        """Extract date range from dataset"""
        date_columns = [col for col in df.columns if any(date_term in col.lower() 
                       for date_term in ['date', 'timestamp', 'time'])]
        
        if date_columns:
            try:
                dates = pd.to_datetime(df[date_columns[0]])
                return f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
            except:
                return "Date parsing error"
        return "No date column found"
    
    def _get_key_metrics(self, df, category):
        """Extract key metrics based on medical condition category"""
        metrics = {}
        
        if category == "cardiovascular":
            if 'systolic_bp' in df.columns:
                metrics['avg_systolic'] = f"{df['systolic_bp'].mean():.1f}"
                metrics['hypertension_cases'] = f"{(df['systolic_bp'] >= 140).sum()}"
            if 'total_cholesterol' in df.columns:
                metrics['avg_cholesterol'] = f"{df['total_cholesterol'].mean():.1f}"
                metrics['high_cholesterol'] = f"{(df['total_cholesterol'] >= 240).sum()}"
        
        elif category == "diabetes":
            if 'glucose_level' in df.columns:
                metrics['avg_glucose'] = f"{df['glucose_level'].mean():.1f}"
                metrics['hyperglycemic_readings'] = f"{(df['glucose_level'] >= 180).sum()}"
                metrics['hypoglycemic_readings'] = f"{(df['glucose_level'] <= 70).sum()}"
        
        elif category == "oncology":
            if 'psa_ng_ml' in df.columns:
                metrics['elevated_psa'] = f"{(df['psa_ng_ml'] >= 4.0).sum()}"
            if 'cancer_type' in df.columns:
                metrics['cancer_types'] = f"{df['cancer_type'].nunique()}"
        
        elif category == "mental_health":
            if 'phq9_score' in df.columns:
                metrics['avg_phq9'] = f"{df['phq9_score'].mean():.1f}"
                metrics['severe_depression'] = f"{(df['phq9_score'] >= 20).sum()}"
            if 'gad7_score' in df.columns:
                metrics['severe_anxiety'] = f"{(df['gad7_score'] >= 15).sum()}"
        
        elif category == "laboratory":
            if 'wbc_count' in df.columns:
                metrics['abnormal_wbc'] = f"{((df['wbc_count'] < 4.0) | (df['wbc_count'] > 11.0)).sum()}"
            if 'hemoglobin' in df.columns:
                metrics['anemia_cases'] = f"{(df['hemoglobin'] < 12.0).sum()}"
        
        elif category == "vital_signs":
            if 'temperature_f' in df.columns:
                metrics['fever_cases'] = f"{(df['temperature_f'] >= 100.4).sum()}"
            if 'heart_rate' in df.columns:
                metrics['avg_heart_rate'] = f"{df['heart_rate'].mean():.1f}"
        
        return metrics
    
    def generate_dataset_report(self):
        """Generate comprehensive dataset report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "dataset_analysis": self.analysis_results,
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        with open(os.path.join(self.datasets_dir, "dataset_analysis_report.json"), 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Dataset analysis report saved to: {self.datasets_dir}/dataset_analysis_report.json")
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations for dataset enhancement"""
        return {
            "immediate_enhancements": [
                "Add respiratory condition datasets (asthma, COPD, pulmonary function)",
                "Include medication interaction datasets",
                "Add imaging data integration (DICOM metadata)",
                "Implement longitudinal patient tracking"
            ],
            "data_quality_improvements": [
                "Add data validation rules for medical ranges",
                "Implement missing data imputation strategies",
                "Add data anonymization and de-identification",
                "Include data provenance tracking"
            ],
            "clinical_integration": [
                "Map to ICD-10 diagnosis codes",
                "Integrate SNOMED CT clinical terminology",
                "Add LOINC codes for laboratory results",
                "Include CPT codes for procedures"
            ],
            "privacy_enhancements": [
                "Implement differential privacy for population statistics",
                "Add homomorphic encryption for sensitive computations",
                "Enhance secure multi-party computation protocols",
                "Add zero-knowledge proof capabilities"
            ]
        }

def main():
    """Main execution function"""
    analyzer = MedicalDatasetAnalyzer()
    
    # Analyze all datasets
    results = analyzer.analyze_all_datasets()
    
    # Generate comprehensive report
    report = analyzer.generate_dataset_report()
    
    print(f"\n✅ Multi-condition dataset analysis complete!")
    print(f"📊 Ready for Phase 2: Condition-Specific Analytics Implementation")

if __name__ == "__main__":
    main()
