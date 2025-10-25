export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  register: `${API_BASE_URL}/register`,
  login: `${API_BASE_URL}/login`,
  upload: `${API_BASE_URL}/upload`,
  uploads: `${API_BASE_URL}/uploads`,
  uploadById: (id) => `${API_BASE_URL}/uploads/${id}`,
  results: (id) => `${API_BASE_URL}/result/${id}`,
  verifyOtp: `${API_BASE_URL}/verify-otp`,
  sendOtp: `${API_BASE_URL}/send-otp`,
  refresh: `${API_BASE_URL}/refresh`,
  me: `${API_BASE_URL}/me`,

  // Enhanced ML endpoints
  enhancedML: `${API_BASE_URL}/enhanced-ml`,
  analyzeML: `${API_BASE_URL}/enhanced-ml/analyze`,
  mlModels: `${API_BASE_URL}/enhanced-ml/models`,
  mlModelById: (id) => `${API_BASE_URL}/enhanced-ml/models/${id}`,

  // Enhanced Federated Learning endpoints
  federatedLearning: `${API_BASE_URL}/federated-learning`,
  initiateFederated: `${API_BASE_URL}/federated-learning/initiate`,
  federatedModels: `${API_BASE_URL}/federated-learning/models`,
  federatedModelById: (id) => `${API_BASE_URL}/federated-learning/models/${id}`,
  joinFederated: (id) => `${API_BASE_URL}/federated-learning/models/${id}/join`,
  submitFederatedUpdate: (id) => `${API_BASE_URL}/federated-learning/models/${id}/update`,
  aggregateFederated: (id) => `${API_BASE_URL}/federated-learning/models/${id}/aggregate`,

  // Enhanced Privacy ML endpoints
  privacyML: `${API_BASE_URL}/privacy-ml/enhanced`,
  trainPrivateModel: `${API_BASE_URL}/privacy-ml/enhanced/train`,
  createPrivateHistogram: `${API_BASE_URL}/privacy-ml/enhanced/histogram`,
  privatePredictions: `${API_BASE_URL}/privacy-ml/enhanced/predictions`,
  privatePredictionById: (id) => `${API_BASE_URL}/privacy-ml/enhanced/predictions/${id}`,

  // Enhanced Secure Computations endpoints
  enhancedSecureComputations: `${API_BASE_URL}/secure-computations/enhanced`,
  createEnhancedComputation: `${API_BASE_URL}/secure-computations/enhanced/create`,
  enhancedComputationById: (id) => `${API_BASE_URL}/secure-computations/enhanced/computations/${id}`,
  joinEnhancedComputation: (id) => `${API_BASE_URL}/secure-computations/enhanced/computations/${id}/join`,
  submitEnhancedData: (id) => `${API_BASE_URL}/secure-computations/enhanced/computations/${id}/submit`,
  performEnhancedComputation: (id) => `${API_BASE_URL}/secure-computations/enhanced/computations/${id}/compute`,
  getEnhancedResult: (id) => `${API_BASE_URL}/secure-computations/enhanced/computations/${id}/result`,
  exportEnhancedResults: (id) => `${API_BASE_URL}/secure-computations/enhanced/computations/${id}/export`,

  // Enhanced Monitoring Analytics endpoints
  enhancedAnalytics: `${API_BASE_URL}/monitoring-analytics/enhanced`,
  mentalHealthAnalytics: `${API_BASE_URL}/monitoring-analytics/enhanced/mental-health`,
  laboratoryAnalytics: `${API_BASE_URL}/monitoring-analytics/enhanced/laboratory`,
  vitalsAnalytics: `${API_BASE_URL}/monitoring-analytics/enhanced/vitals`,
  riskAnalytics: `${API_BASE_URL}/monitoring-analytics/enhanced/risk`,

  // Legacy endpoints (keeping for backward compatibility)
  analytics: `${API_BASE_URL}/analytics`,
  secureComputations: `${API_BASE_URL}/secure-computations/computations`,
  createComputation: `${API_BASE_URL}/secure-computations/create`,
  secureComputationById: (id) => `${API_BASE_URL}/secure-computations/computations/${id}`,
  computationDetails: (id) => `${API_BASE_URL}/secure-computations/computations/${id}`,
  joinComputation: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/join`,
  submitData: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/submit`,
  userSubmission: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/user-submission`,
  mySubmission: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/my-submission`,
  deleteSubmission: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/delete-submission`,
  performComputation: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/compute`,
  exportResults: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/export`,
  activeParticipants: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/active-participants`,
  pendingComputationRequests: `${API_BASE_URL}/secure-computations/pending-requests`,
  acceptComputationRequest: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/accept`,
  declineComputationRequest: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/decline`,
  deleteComputation: (id) => `${API_BASE_URL}/secure-computations/computations/${id}`,
  inviteParticipant: (id) => `${API_BASE_URL}/secure-computations/computations/${id}/invite`,
  computationResult: (id) => `${API_BASE_URL}/computations/${id}`,
  secureComputationOrganizations: `${API_BASE_URL}/secure-computations/organizations`,
  availableComputations: `${API_BASE_URL}/secure-computations/available-computations`,

  // Report request endpoints
  reportRequests: `${API_BASE_URL}/report-requests`,
  reportRequestById: (id) => `${API_BASE_URL}/report-requests/${id}`,
  uploadReport: (id) => `${API_BASE_URL}/report-requests/${id}/upload`,
  downloadReport: (id) => `${API_BASE_URL}/report-requests/${id}/download`,
  healthcareOrganizations: `${API_BASE_URL}/healthcare-organizations`,
};

export const fetchApi = async (endpoint, options = {}, retryWithNewToken = true) => {
  try {
    const headers = { ...options.headers };

    // Only set Content-Type for non-GET requests if not already set and body is not FormData
    if (options.method !== 'GET' && !headers['Content-Type'] && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (options.token) {
      headers.Authorization = `Bearer ${options.token}`;
    }

    // Perform the fetch call
    const response = await fetch(endpoint, {
      ...options,
      headers,
      // Include credentials by default to support cookie-based auth flows
      credentials: options.credentials ?? 'include',
    });

    // Handle non-JSON responses (like file downloads)
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      // For non-JSON responses, try to parse as JSON first, fallback to text
      try {
        const text = await response.text();
        data = text ? JSON.parse(text) : {};
      } catch {
        data = { message: 'Response received' };
      }
    }

    if (!response.ok) {
      // Handle authentication issues with token refresh
      if (response.status === 401 && retryWithNewToken) {
        // Try to refresh the token via refresh endpoint
        try {
          const refreshResp = await fetch(API_ENDPOINTS.refresh, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          });

          if (refreshResp.ok) {
            const refreshData = await refreshResp.json();
            const newToken = refreshData?.access_token || refreshData?.token || refreshData?.accessToken;
            if (newToken) {
              // Retry original request with the new token, but avoid infinite loops
              return await fetchApi(endpoint, { ...options, token: newToken }, false);
            }
          }
        } catch (e) {
          // Ignore refresh errors and fall through to normal error handling
        }
      }
      const errorMessage =
        data?.message || data?.detail || `Request failed with status ${response.status}`;
      const errorCode = data?.error_code || data?.code;
      const serverDetail = data?.server_detail || data?.error || null;
      const error = new Error(errorMessage);
      error.status = response.status;
      if (errorCode) error.error_code = errorCode;
      if (serverDetail) error.server_detail = serverDetail;
      throw error;
    }

    return data;
  } catch (error) {
    if (error.message === 'Failed to fetch') {
      throw new Error('Network error - Please check if the backend server is running');
    }
    throw error;
  }
};