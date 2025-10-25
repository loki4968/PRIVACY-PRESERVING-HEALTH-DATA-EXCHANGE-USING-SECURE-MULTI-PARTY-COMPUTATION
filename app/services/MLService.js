import axios from 'axios';
import { getAuthHeader } from '../utils/auth';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';

export const MLService = {
  // Enhanced ML Analysis
  analyzeData: async (data, analysisType, parameters = {}) => {
    const response = await axios.post(
      API_ENDPOINTS.analyzeML,
      { data, analysis_type: analysisType, parameters },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  getModels: async () => {
    const response = await axios.get(
      API_ENDPOINTS.mlModels,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  getModelById: async (modelId) => {
    const response = await axios.get(
      API_ENDPOINTS.mlModelById(modelId),
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Enhanced Federated Learning
  initializeFederatedModel: async (modelType, parameters, privacyBudget = 1.0) => {
    const response = await axios.post(
      API_ENDPOINTS.initiateFederated,
      { model_type: modelType, parameters, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  joinFederatedTraining: async (modelId, organizationId) => {
    const response = await axios.post(
      API_ENDPOINTS.joinFederated(modelId),
      { organization_id: organizationId },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  submitModelUpdate: async (modelId, organizationId, gradients, metrics) => {
    const response = await axios.post(
      API_ENDPOINTS.submitFederatedUpdate(modelId),
      { organization_id: organizationId, gradients, metrics },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  aggregateModelUpdates: async (modelId) => {
    const response = await axios.post(
      API_ENDPOINTS.aggregateFederated(modelId),
      {},
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  getFederatedModels: async () => {
    const response = await axios.get(
      API_ENDPOINTS.federatedModels,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Enhanced Privacy-Preserving ML
  trainPrivateModel: async (modelType, features, labels, privacyBudget) => {
    const response = await axios.post(
      API_ENDPOINTS.trainPrivateModel,
      { model_type: modelType, features, labels, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  createPrivateHistogram: async (data, bins, privacyBudget) => {
    const response = await axios.post(
      API_ENDPOINTS.createPrivateHistogram,
      { data, bins, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  getPrivatePredictions: async () => {
    const response = await axios.get(
      API_ENDPOINTS.privatePredictions,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Enhanced Secure ML Integration
  createSecureMLComputation: async (computationType, modelType, securityMethod, parameters) => {
    const response = await axios.post(
      API_ENDPOINTS.createEnhancedComputation,
      { computation_type: computationType, model_type: modelType, security_method: securityMethod, parameters },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  joinSecureMLComputation: async (computationId, organizationId) => {
    const response = await axios.post(
      API_ENDPOINTS.joinEnhancedComputation(computationId),
      { organization_id: organizationId },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  submitDataForSecureML: async (computationId, organizationId, data) => {
    const response = await axios.post(
      API_ENDPOINTS.submitEnhancedData(computationId),
      { organization_id: organizationId, data },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  getSecureMLResult: async (computationId, organizationId) => {
    const response = await axios.get(
      API_ENDPOINTS.getEnhancedResult(computationId),
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Time Series Forecasting
  forecastTimeSeries: async (timeSeries, horizon, method, privacyBudget) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/timeseries/forecast`,
      { time_series: timeSeries, horizon, method, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  detectTimeSeriesAnomalies: async (timeSeries, privacyBudget) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/timeseries/anomalies`,
      { time_series: timeSeries, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  analyzeTimeSeriesSeasonality: async (timeSeries, privacyBudget) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/timeseries/seasonality`,
      { time_series: timeSeries, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Risk Stratification
  calculateRiskScore: async (metrics, patientInfo, privacyBudget) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/risk/assessment`,
      { metrics, patient_info: patientInfo, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  identifyRiskFactors: async (metrics, timestamps, privacyBudget) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/risk/factors`,
      { metrics, timestamps, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  createRiskModel: async (trainingData, features, target, modelType, privacyBudget) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/risk/model`,
      { training_data: trainingData, features, target, model_type: modelType, privacy_budget: privacyBudget },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  predictRisk: async (modelId, patientData) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/risk/predict/${modelId}`,
      patientData,
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Anomaly Detection
  detectAnomalies: async (data, method, threshold) => {
    const response = await axios.post(
      `${API_ENDPOINTS.enhancedML}/anomalies/detect`,
      { data, method, threshold },
      { headers: getAuthHeader() }
    );
    return response.data;
  },
};

export default MLService;