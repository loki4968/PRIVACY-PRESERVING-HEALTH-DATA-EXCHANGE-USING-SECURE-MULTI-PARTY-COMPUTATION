from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

# Import local modules
from services.machine_learning import FederatedLearningService, PrivacyPreservingML, SecureModelInference, AnomalyDetectionService
from services.privacy_ml_integration import PrivacyPreservingMLIntegration, TimeSeriesForecastingService, RiskStratificationService
from services.time_series_forecasting import TimeSeriesForecasting
from services.risk_stratification import RiskStratificationService as RiskService
from dependencies import get_current_user
from models import Organization as User  # Using Organization as User model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/ml",
    tags=["Machine Learning"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
federated_learning_service = FederatedLearningService()
privacy_ml_service = PrivacyPreservingML()
secure_inference_service = SecureModelInference()
anomaly_detection_service = AnomalyDetectionService()
privacy_ml_integration = PrivacyPreservingMLIntegration()
time_series_forecasting = TimeSeriesForecasting()
risk_stratification = RiskService()

# Pydantic models for request/response validation
class ModelInitRequest(BaseModel):
    model_type: str = Field(..., description="Type of model to initialize (linear, logistic, forest, isolation_forest, kmeans)")
    parameters: Dict[str, Any] = Field(default={}, description="Additional parameters for model initialization")

class ModelUpdateRequest(BaseModel):
    gradients: Dict[str, Any] = Field(..., description="Model gradients or parameters")
    metrics: Dict[str, Any] = Field(default={}, description="Training metrics")

class SecureComputationRequest(BaseModel):
    computation_type: str = Field(..., description="Type of computation (federated_learning, private_training, secure_inference)")
    model_type: str = Field(..., description="Type of ML model")
    security_method: str = Field(..., description="Security method (standard, homomorphic, hybrid)")
    parameters: Dict[str, Any] = Field(default={}, description="Additional parameters")

class TimeSeriesDataPoint(BaseModel):
    timestamp: str = Field(..., description="Timestamp in format YYYY-MM-DD HH:MM:SS")
    value: float = Field(..., description="Value at the timestamp")

class TimeSeriesForecastRequest(BaseModel):
    time_series: List[TimeSeriesDataPoint] = Field(..., description="Time series data points")
    horizon: int = Field(default=7, description="Number of future points to forecast")
    method: str = Field(default="linear", description="Forecasting method (linear, exponential_smoothing, holt_winters, comprehensive)")
    privacy_budget: float = Field(default=1.0, description="Privacy budget for differential privacy")

class RiskAssessmentRequest(BaseModel):
    metrics: Dict[str, List[float]] = Field(..., description="Dictionary of health metrics")
    patient_info: Dict[str, Any] = Field(default={}, description="Additional patient information")
    privacy_budget: float = Field(default=1.0, description="Privacy budget for differential privacy")

class AnomalyDetectionRequest(BaseModel):
    data: List[float] = Field(..., description="Data points to analyze for anomalies")
    method: str = Field(default="z_score", description="Anomaly detection method")
    threshold: float = Field(default=2.0, description="Threshold for anomaly detection")

# Federated Learning endpoints
@router.post("/federated/initialize", response_model=Dict[str, Any])
async def initialize_federated_model(
    request: ModelInitRequest,
    current_user: User = Depends(get_current_user)
):
    """Initialize a new federated learning model."""
    try:
        model_id = federated_learning_service.initialize_model(
            request.model_type, request.parameters)
        
        return {
            "success": True,
            "model_id": model_id,
            "model_type": request.model_type
        }
    except Exception as e:
        logger.error(f"Error initializing federated model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/federated/{model_id}/join", response_model=Dict[str, Any])
async def join_federated_training(
    model_id: str = Path(..., description="ID of the federated model"),
    organization_id: int = Query(..., description="ID of the organization joining"),
    current_user: User = Depends(get_current_user)
):
    """Join a federated learning training session."""
    try:
        result = federated_learning_service.join_federated_training(model_id, organization_id)
        return {"success": True, "model_id": model_id, "organization_id": organization_id}
    except Exception as e:
        logger.error(f"Error joining federated training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/federated/{model_id}/update", response_model=Dict[str, Any])
async def submit_model_update(
    request: ModelUpdateRequest,
    model_id: str = Path(..., description="ID of the federated model"),
    organization_id: int = Query(..., description="ID of the organization submitting update"),
    current_user: User = Depends(get_current_user)
):
    """Submit a model update for federated learning."""
    try:
        result = federated_learning_service.submit_model_update(
            model_id, organization_id, request.gradients, request.metrics)
        
        return {"success": True, "model_id": model_id, "organization_id": organization_id}
    except Exception as e:
        logger.error(f"Error submitting model update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/federated/{model_id}/aggregate", response_model=Dict[str, Any])
async def aggregate_model_updates(
    model_id: str = Path(..., description="ID of the federated model"),
    current_user: User = Depends(get_current_user)
):
    """Aggregate model updates for federated learning."""
    try:
        result = federated_learning_service.aggregate_model_updates(model_id)
        return result
    except Exception as e:
        logger.error(f"Error aggregating model updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/federated/models", response_model=List[Dict[str, Any]])
async def get_federated_models(
    current_user: User = Depends(get_current_user)
):
    """Get a list of all available federated models."""
    try:
        models = await federated_learning_service.get_federated_models()
        return models
    except Exception as e:
        logger.error(f"Error getting federated models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Privacy-Preserving ML endpoints
@router.post("/privacy/train", response_model=Dict[str, Any])
async def train_private_model(
    model_type: str = Query(..., description="Type of model to train (linear, logistic)"),
    features: List[List[float]] = Body(..., description="Feature matrix"),
    labels: List[float] = Body(..., description="Target labels"),
    privacy_budget: float = Query(1.0, description="Privacy budget for differential privacy"),
    current_user: User = Depends(get_current_user)
):
    """Train a privacy-preserving machine learning model."""
    try:
        import numpy as np
        X = np.array(features)
        y = np.array(labels)
        
        result = privacy_ml_service.train_private_model(model_type, X, y, privacy_budget)
        return result
    except Exception as e:
        logger.error(f"Error training private model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/privacy/histogram", response_model=Dict[str, Any])
async def create_private_histogram(
    data: List[float] = Body(..., description="Data points"),
    bins: int = Query(10, description="Number of bins"),
    privacy_budget: float = Query(1.0, description="Privacy budget for differential privacy"),
    current_user: User = Depends(get_current_user)
):
    """Create a privacy-preserving histogram."""
    try:
        result = privacy_ml_service.private_histogram(data, bins, privacy_budget)
        return result
    except Exception as e:
        logger.error(f"Error creating private histogram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Secure ML Integration endpoints
@router.post("/secure/create", response_model=Dict[str, Any])
async def create_secure_ml_computation(
    request: SecureComputationRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new secure ML computation."""
    try:
        result = privacy_ml_integration.create_secure_ml_computation(
            request.computation_type,
            request.model_type,
            request.security_method,
            request.parameters
        )
        return result
    except Exception as e:
        logger.error(f"Error creating secure ML computation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/secure/{computation_id}/join", response_model=Dict[str, Any])
async def join_secure_ml_computation(
    computation_id: str = Path(..., description="ID of the secure computation"),
    organization_id: int = Query(..., description="ID of the organization joining"),
    current_user: User = Depends(get_current_user)
):
    """Join a secure ML computation."""
    try:
        result = privacy_ml_integration.join_secure_ml_computation(computation_id, organization_id)
        return result
    except Exception as e:
        logger.error(f"Error joining secure ML computation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/secure/{computation_id}/submit", response_model=Dict[str, Any])
async def submit_data_for_secure_ml(
    data: Dict[str, Any] = Body(..., description="Data for the computation"),
    computation_id: str = Path(..., description="ID of the secure computation"),
    organization_id: int = Query(..., description="ID of the organization submitting data"),
    current_user: User = Depends(get_current_user)
):
    """Submit data for a secure ML computation."""
    try:
        result = privacy_ml_integration.submit_data_for_secure_ml(
            computation_id, organization_id, data)
        return result
    except Exception as e:
        logger.error(f"Error submitting data for secure ML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/secure/{computation_id}/result", response_model=Dict[str, Any])
async def get_secure_ml_result(
    computation_id: str = Path(..., description="ID of the secure computation"),
    organization_id: int = Query(..., description="ID of the organization requesting results"),
    current_user: User = Depends(get_current_user)
):
    """Get the result of a secure ML computation."""
    try:
        result = privacy_ml_integration.get_secure_ml_result(computation_id, organization_id)
        return result
    except Exception as e:
        logger.error(f"Error getting secure ML result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Time Series Forecasting endpoints
@router.post("/timeseries/forecast", response_model=Dict[str, Any])
async def forecast_time_series(
    request: TimeSeriesForecastRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate forecasts for time series data."""
    try:
        # Convert Pydantic model to dictionary format expected by service
        time_series_data = [dict(point) for point in request.time_series]
        
        if request.method == "linear":
            result = time_series_forecasting.forecast_linear(
                time_series_data, request.horizon, request.privacy_budget)
        elif request.method == "exponential_smoothing":
            result = time_series_forecasting.forecast_exponential_smoothing(
                time_series_data, request.horizon, privacy_budget=request.privacy_budget)
        elif request.method == "holt_winters":
            result = time_series_forecasting.forecast_holt_winters(
                time_series_data, request.horizon, privacy_budget=request.privacy_budget)
        elif request.method == "comprehensive":
            result = time_series_forecasting.generate_comprehensive_forecast(
                time_series_data, request.horizon, request.privacy_budget)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported forecasting method: {request.method}")
        
        return result
    except Exception as e:
        logger.error(f"Error in time series forecasting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/timeseries/anomalies", response_model=Dict[str, Any])
async def detect_time_series_anomalies(
    request: TimeSeriesForecastRequest,
    current_user: User = Depends(get_current_user)
):
    """Detect anomalies in time series data."""
    try:
        # Convert Pydantic model to dictionary format expected by service
        time_series_data = [dict(point) for point in request.time_series]
        
        result = time_series_forecasting.detect_anomalies(
            time_series_data, method="z_score", threshold=2.0, privacy_budget=request.privacy_budget)
        
        return result
    except Exception as e:
        logger.error(f"Error in anomaly detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/timeseries/seasonality", response_model=Dict[str, Any])
async def analyze_time_series_seasonality(
    request: TimeSeriesForecastRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze seasonality patterns in time series data."""
    try:
        # Convert Pydantic model to dictionary format expected by service
        time_series_data = [dict(point) for point in request.time_series]
        
        result = time_series_forecasting.analyze_seasonality(
            time_series_data, max_period=30, privacy_budget=request.privacy_budget)
        
        return result
    except Exception as e:
        logger.error(f"Error in seasonality analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Risk Stratification endpoints
@router.post("/risk/assessment", response_model=Dict[str, Any])
async def calculate_risk_score(
    request: RiskAssessmentRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculate risk score for a patient."""
    try:
        result = risk_stratification.calculate_risk_score(
            request.metrics, request.patient_info, request.privacy_budget)
        
        return result
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/factors", response_model=Dict[str, Any])
async def identify_risk_factors(
    request: RiskAssessmentRequest,
    timestamps: Dict[str, List[str]] = Body(default=None, description="Optional timestamps for each metric"),
    current_user: User = Depends(get_current_user)
):
    """Identify specific risk factors in health metrics."""
    try:
        result = risk_stratification.identify_risk_factors(
            request.metrics, timestamps, request.privacy_budget)
        
        return result
    except Exception as e:
        logger.error(f"Error in risk factor identification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/model", response_model=Dict[str, Any])
async def create_risk_model(
    training_data: List[Dict[str, Any]] = Body(..., description="Training data for risk model"),
    features: List[str] = Body(..., description="Feature names to use for prediction"),
    target: str = Query("risk_category", description="Target variable to predict"),
    model_type: str = Query("logistic", description="Type of model to create"),
    privacy_budget: float = Query(1.0, description="Privacy budget for differential privacy"),
    current_user: User = Depends(get_current_user)
):
    """Create a risk prediction model."""
    try:
        result = risk_stratification.create_risk_model(
            training_data, features, target, model_type, privacy_budget)
        
        return result
    except Exception as e:
        logger.error(f"Error in risk model creation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/predict/{model_id}", response_model=Dict[str, Any])
async def predict_risk(
    patient_data: Dict[str, Any] = Body(..., description="Patient data for prediction"),
    model_id: str = Path(..., description="ID of the risk model to use"),
    current_user: User = Depends(get_current_user)
):
    """Predict risk using a previously created risk model."""
    try:
        result = risk_stratification.predict_risk(model_id, patient_data)
        
        return result
    except Exception as e:
        logger.error(f"Error in risk prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Anomaly Detection endpoints
@router.post("/anomalies/detect", response_model=Dict[str, Any])
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    current_user: User = Depends(get_current_user)
):
    """Detect anomalies in data."""
    try:
        result = anomaly_detection_service.detect_anomalies(
            request.data, request.method, request.threshold)
        
        return result
    except Exception as e:
        logger.error(f"Error in anomaly detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))