import { API_ENDPOINTS, fetchApi } from '../config/api';
import { getToken } from '../utils/sessionManager';

export const getHealthcareOrganizations = async () => {
  const token = getToken();
  return fetchApi(API_ENDPOINTS.healthcareOrganizations, {
    method: 'GET',
    token,
  });
};

export const createReportRequest = async (requestData) => {
  const token = getToken();
  return fetchApi(API_ENDPOINTS.reportRequests, {
    method: 'POST',
    body: JSON.stringify(requestData),
    token,
  });
};

export const getReportRequests = async (status = null) => {
  const token = getToken();
  let endpoint = API_ENDPOINTS.reportRequests;
  if (status) {
    endpoint += `?status=${status}`;
  }
  return fetchApi(endpoint, {
    method: 'GET',
    token,
  });
};

export const getReportRequestById = async (requestId) => {
  const token = getToken();
  return fetchApi(API_ENDPOINTS.reportRequestById(requestId), {
    method: 'GET',
    token,
  });
};

export const updateReportRequest = async (requestId, updateData) => {
  const token = getToken();
  return fetchApi(API_ENDPOINTS.reportRequestById(requestId), {
    method: 'PUT',
    body: JSON.stringify(updateData),
    token,
  });
};

export const uploadReportFile = async (requestId, file) => {
  const token = getToken();
  const formData = new FormData();
  formData.append('file', file);
  
  return fetch(API_ENDPOINTS.uploadReport(requestId), {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  }).then(response => {
    if (!response.ok) {
      return response.json().then(err => Promise.reject(err));
    }
    return response.json();
  });
};

export const downloadReportFile = (requestId) => {
  const token = getToken();
  window.open(`${API_ENDPOINTS.downloadReport(requestId)}?token=${token}`, '_blank');
};