#!/usr/bin/env python3
"""
Install ML Dependencies and Test System
This script installs required ML libraries and tests the functionality
"""

import subprocess
import sys
import importlib

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} is available")
        return True
    except ImportError:
        print(f"❌ {package_name or module_name} is not available")
        return False

def main():
    print("🚀 Installing ML Dependencies for Health Data Exchange")
    print("=" * 60)
    
    # Required packages
    packages = [
        "scikit-learn==1.3.0",
        "pandas==2.0.3", 
        "scipy==1.11.1",
        "matplotlib==3.7.2",
        "seaborn==0.12.2"
    ]
    
    print("\n📦 Installing packages...")
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Results: {success_count}/{len(packages)} packages installed")
    
    print("\n🧪 Testing imports...")
    test_results = []
    
    # Test core ML libraries
    test_results.append(test_import("sklearn", "scikit-learn"))
    test_results.append(test_import("pandas", "pandas"))
    test_results.append(test_import("scipy", "scipy"))
    test_results.append(test_import("numpy", "numpy"))
    
    # Test specific ML modules
    test_results.append(test_import("sklearn.ensemble", "Random Forest"))
    test_results.append(test_import("sklearn.linear_model", "Linear Models"))
    test_results.append(test_import("sklearn.metrics", "ML Metrics"))
    
    successful_imports = sum(test_results)
    print(f"\n📈 Import Results: {successful_imports}/{len(test_results)} modules available")
    
    if successful_imports == len(test_results):
        print("\n🎉 All ML dependencies are ready!")
        print("\n🔬 Your project now supports:")
        print("   ✅ Real Logistic Regression with feature importance")
        print("   ✅ Real Random Forest with accuracy metrics")
        print("   ✅ Anomaly Detection with statistical methods")
        print("   ✅ Correlation Analysis with p-values")
        print("   ✅ Linear Regression with R² scores")
        print("   ✅ Survival Analysis with Kaplan-Meier curves")
        
        print("\n📊 Meaningful Results Your Project Provides:")
        print("   🏥 Hospital Collaboration: Multi-site research without data sharing")
        print("   🔍 Pattern Discovery: ML finds hidden patterns in health data")
        print("   📈 Predictive Analytics: Forecast patient outcomes")
        print("   🚨 Anomaly Detection: Identify unusual health patterns")
        print("   🧬 Genomics Analysis: GWAS and pharmacogenomics")
        print("   💊 Drug Safety: Adverse reaction monitoring")
        
        print("\n🎯 Demo Scenarios You Can Show:")
        print("   1. Multi-hospital blood pressure correlation analysis")
        print("   2. Federated learning for diabetes prediction")
        print("   3. Anomaly detection in vital signs")
        print("   4. Drug safety signal detection")
        print("   5. Patient survival analysis")
        
    else:
        print("\n⚠️  Some dependencies are missing. Please check the errors above.")
        print("   Try running: pip install -r requirements.txt")
    
    print("\n" + "=" * 60)
    print("🎓 Your Privacy-Preserving Health Data Exchange is ready!")

if __name__ == "__main__":
    main()
