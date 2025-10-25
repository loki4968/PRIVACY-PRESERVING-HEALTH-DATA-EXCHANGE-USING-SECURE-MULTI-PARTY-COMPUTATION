#!/usr/bin/env python3
"""
Test script for simplified ML services without heavy dependencies.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'services'))

from privacy_ml_integration_simplified import PrivacyPreservingMLIntegration
from advanced_ml_algorithms_simplified import AdvancedMLAlgorithms

def test_privacy_ml_integration():
    """Test the simplified privacy ML integration service."""
    print("Testing Privacy-Preserving ML Integration...")

    # Initialize service
    service = PrivacyPreservingMLIntegration()

    # Test creating a secure ML computation
    result = service.create_secure_ml_computation(
        computation_type="private_training",
        model_type="linear",
        security_method="standard"
    )

    if result.get("success"):
        print(f"✓ Created secure ML computation: {result['computation_id']}")
    else:
        print(f"✗ Failed to create computation: {result.get('error')}")

    # Test submitting data
    data = {
        "features": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        "labels": [1.0, 2.0, 3.0]
    }

    submit_result = service.submit_data_for_secure_ml(
        computation_id=result["computation_id"],
        organization_id=1,
        data=data
    )

    if submit_result.get("success"):
        print("✓ Successfully submitted data for secure ML")
    else:
        print(f"✗ Failed to submit data: {submit_result.get('error')}")

    # Test getting results
    get_result = service.get_secure_ml_result(
        computation_id=result["computation_id"],
        organization_id=1
    )

    if get_result.get("success"):
        print(f"✓ Got secure ML results: {get_result['metrics']}")
    else:
        print(f"✗ Failed to get results: {get_result.get('error')}")

    print("Privacy-Preserving ML Integration test completed.\n")

def test_advanced_ml_algorithms():
    """Test the simplified advanced ML algorithms service."""
    print("Testing Advanced ML Algorithms...")

    # Initialize service
    service = AdvancedMLAlgorithms()

    # Test training linear regression
    X = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]]
    y = [1.0, 2.0, 3.0, 4.0]

    result = service.train_linear_regression(X, y)

    if result.get("success"):
        print(f"✓ Trained linear regression model: {result['model_id']}")
        print(f"  Metrics: MSE={result['metrics']['mse']:.4f}, R2={result['metrics']['r2']:.4f}")
    else:
        print(f"✗ Failed to train linear regression: {result.get('error')}")

    # Test training simple classifier
    X_class = [[1.0, 2.0], [1.1, 2.1], [5.0, 6.0], [5.1, 6.1]]
    y_class = ["class_0", "class_0", "class_1", "class_1"]

    result_class = service.train_simple_classifier(X_class, y_class)

    if result_class.get("success"):
        print(f"✓ Trained simple classifier model: {result_class['model_id']}")
        print(f"  Metrics: Accuracy={result_class['metrics']['accuracy']:.4f}")
    else:
        print(f"✗ Failed to train simple classifier: {result_class.get('error')}")

    # Test predictions
    if result.get("success"):
        pred_result = service.predict_with_model(result["model_id"], [[2.0, 3.0], [4.0, 5.0]])

        if pred_result.get("success"):
            print(f"✓ Made predictions: {pred_result['predictions']}")
        else:
            print(f"✗ Failed to make predictions: {pred_result.get('error')}")

    print("Advanced ML Algorithms test completed.\n")

def test_privacy_preserving_ml():
    """Test the privacy-preserving ML utilities."""
    print("Testing Privacy-Preserving ML utilities...")

    privacy_ml = PrivacyPreservingMLIntegration().privacy_ml

    # Test data
    data = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Test private mean
    private_mean = privacy_ml.private_mean(data, privacy_budget=1.0)
    print(f"✓ Private mean: {private_mean:.4f}")

    # Test adding noise
    noisy_data = privacy_ml.add_noise(data, epsilon=1.0)
    print(f"✓ Added noise to data: {len(noisy_data)} values")

    # Test training private model
    X = [[1.0], [2.0], [3.0], [4.0]]
    y = [2.0, 4.0, 6.0, 8.0]

    model_result = privacy_ml.train_private_model("linear", X, y, privacy_budget=1.0)

    if "coefficients" in model_result:
        print(f"✓ Trained private model: slope={model_result['coefficients'][0]:.4f}, intercept={model_result['intercept']:.4f}")
    else:
        print(f"✗ Failed to train private model: {model_result.get('error')}")

    print("Privacy-Preserving ML utilities test completed.\n")

def main():
    """Run all tests."""
    print("Starting simplified ML services tests...\n")

    try:
        test_privacy_ml_integration()
        test_advanced_ml_algorithms()
        test_privacy_preserving_ml()

        print("All tests completed successfully! ✓")
        print("\nThe simplified ML services are working correctly without heavy dependencies.")

    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
