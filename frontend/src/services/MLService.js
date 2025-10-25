import axios from 'axios';
import { getAuthHeader } from '../utils/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const MLService = {
  // Federated Learning
  initializeFederatedModel: async (modelType, parameters) => {
    const response = await axios.post(
      `${API_URL}/api/ml/federated/initialize`,
      { model_type: modelType, parameters },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  joinFederatedTraining: async (modelId, organizationId) => {
    const response = await axios.post(
      `${API_URL}/api/ml/federated/${modelId}/join?organization_id=${organizationId}`,
      {},
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  submitModelUpdate: async (modelId, organizationId, gradients, metrics) => {
    const response = await axios.post(
      `${API_URL}/api/ml/federated/${modelId}/update?organization_id=${organizationId}`,
      { gradients, metrics },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  aggregateModelUpdates: async (modelId) => {
    const response = await axios.get(
      `${API_URL}/api/ml/federated/${modelId}/aggregate`,
      { headers: getAuthHeader() }
    );
    return response.data;
  },
  
  getFederatedModels: async () => {
    const response = await axios.get(
      `${API_URL}/api/ml/federated/models`,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Privacy-Preserving ML
  trainPrivateModel: async (modelType, features, labels, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/privacy/train?model_type=${modelType}&privacy_budget=${privacyBudget}`,
      { features, labels },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  createPrivateHistogram: async (data, bins, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/privacy/histogram?bins=${bins}&privacy_budget=${privacyBudget}`,
      { data },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Secure ML Integration
  createSecureMLComputation: async (computationType, modelType, securityMethod, parameters) => {
    const response = await axios.post(
      `${API_URL}/api/ml/secure/create`,
      { computation_type: computationType, model_type: modelType, security_method: securityMethod, parameters },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  joinSecureMLComputation: async (computationId, organizationId) => {
    const response = await axios.post(
      `${API_URL}/api/ml/secure/${computationId}/join?organization_id=${organizationId}`,
      {},
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  submitDataForSecureML: async (computationId, organizationId, data) => {
    const response = await axios.post(
      `${API_URL}/api/ml/secure/${computationId}/submit?organization_id=${organizationId}`,
      data,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  getSecureMLResult: async (computationId, organizationId) => {
    const response = await axios.get(
      `${API_URL}/api/ml/secure/${computationId}/result?organization_id=${organizationId}`,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Time Series Forecasting
  forecastTimeSeries: async (timeSeries, horizon, method, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/timeseries/forecast`,
      { time_series: timeSeries, horizon, method, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  detectTimeSeriesAnomalies: async (timeSeries, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/timeseries/anomalies`,
      { time_series: timeSeries, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  analyzeTimeSeriesSeasonality: async (timeSeries, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/timeseries/seasonality`,
      { time_series: timeSeries, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Risk Stratification
  calculateRiskScore: async (metrics, patientInfo, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/risk/assessment`,
      { metrics, patient_info: patientInfo, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  identifyRiskFactors: async (metrics, timestamps, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/risk/factors`,
      { metrics, timestamps, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  createRiskModel: async (trainingData, features, target, modelType, privacyBudget) => {
    const response = await axios.post(
      `${API_URL}/api/ml/risk/model?target=${target}&model_type=${modelType}&privacy_budget=${privacyBudget}`,
      { training_data: trainingData, features },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  predictRisk: async (modelId, patientData) => {
    const response = await axios.post(
      `${API_URL}/api/ml/risk/predict/${modelId}`,
      patientData,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Anomaly Detection
  detectAnomalies: async (data, method, threshold) => {
    const response = await axios.post(
      `${API_URL}/api/ml/anomalies/detect`,
      { data, method, threshold },
      { headers: getAuthHeader() }
    );
    return response.data;
  },
};

export default MLService;