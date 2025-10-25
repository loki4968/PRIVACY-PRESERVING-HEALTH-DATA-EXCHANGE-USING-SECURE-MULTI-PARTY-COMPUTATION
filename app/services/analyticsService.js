import { API_BASE_URL, fetchApi, API_ENDPOINTS } from '../config/api';

export const analyticsService = {
  // -------------------- Enhanced Mental Health Analytics -------------------- //
  phq9: async (responses, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.mentalHealthAnalytics + '/phq9', {
          method: 'POST',
          body: JSON.stringify({ responses }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced mental health endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/mental-health/phq9`, {
          method: 'POST',
          body: JSON.stringify({ responses }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing PHQ-9:', error);
      throw error;
    }
  },

  gad7: async (responses, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.mentalHealthAnalytics + '/gad7', {
          method: 'POST',
          body: JSON.stringify({ responses }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced mental health endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/mental-health/gad7`, {
          method: 'POST',
          body: JSON.stringify({ responses }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing GAD-7:', error);
      throw error;
    }
  },

  suicideRisk: async (phq9_responses, risk_flags = {}, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.mentalHealthAnalytics + '/suicide-risk', {
          method: 'POST',
          body: JSON.stringify({ phq9_responses, risk_flags }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced mental health endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/mental-health/suicide-risk`, {
          method: 'POST',
          body: JSON.stringify({ phq9_responses, risk_flags }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing suicide risk:', error);
      throw error;
    }
  },

  treatmentResponse: async (series, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.mentalHealthAnalytics + '/treatment-response', {
          method: 'POST',
          body: JSON.stringify({ series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced mental health endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/mental-health/response`, {
          method: 'POST',
          body: JSON.stringify({ series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing treatment response:', error);
      throw error;
    }
  },

  // -------------------- Enhanced Laboratory Analytics -------------------- //
  cbc: async (cbc, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.laboratoryAnalytics + '/cbc', {
          method: 'POST',
          body: JSON.stringify({ cbc }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced laboratory endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/labs/cbc`, {
          method: 'POST',
          body: JSON.stringify({ cbc }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing CBC:', error);
      throw error;
    }
  },

  cmp: async (cmp, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.laboratoryAnalytics + '/cmp', {
          method: 'POST',
          body: JSON.stringify({ cmp }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced laboratory endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/labs/cmp`, {
          method: 'POST',
          body: JSON.stringify({ cmp }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing CMP:', error);
      throw error;
    }
  },

  infectionMarkers: async (markers, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.laboratoryAnalytics + '/infection-markers', {
          method: 'POST',
          body: JSON.stringify({ markers }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced laboratory endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/labs/markers`, {
          method: 'POST',
          body: JSON.stringify({ markers }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing infection markers:', error);
      throw error;
    }
  },

  labsSummary: async ({ cbc, cmp, markers }, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.laboratoryAnalytics + '/summary', {
          method: 'POST',
          body: JSON.stringify({ cbc, cmp, markers }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced laboratory endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/labs/summary`, {
          method: 'POST',
          body: JSON.stringify({ cbc, cmp, markers }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error generating lab summary:', error);
      throw error;
    }
  },

  // -------------------- Enhanced Vitals Analytics -------------------- //
  temperature: async (series, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.vitalsAnalytics + '/temperature', {
          method: 'POST',
          body: JSON.stringify({ series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced vitals endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/vitals/temperature`, {
          method: 'POST',
          body: JSON.stringify({ series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing temperature:', error);
      throw error;
    }
  },

  sirs: async (vitals, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.vitalsAnalytics + '/sirs', {
          method: 'POST',
          body: JSON.stringify({ vitals }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced vitals endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/vitals/sirs`, {
          method: 'POST',
          body: JSON.stringify({ vitals }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing SIRS:', error);
      throw error;
    }
  },

  bmi: async (height_cm, weight_kg, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.vitalsAnalytics + '/bmi', {
          method: 'POST',
          body: JSON.stringify({ height_cm, weight_kg }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced vitals endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/vitals/bmi`, {
          method: 'POST',
          body: JSON.stringify({ height_cm, weight_kg }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error calculating BMI:', error);
      throw error;
    }
  },

  bmiTrend: async (height_cm, weight_series, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.vitalsAnalytics + '/bmi-trend', {
          method: 'POST',
          body: JSON.stringify({ height_cm, weight_series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced vitals endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/vitals/bmi-trend`, {
          method: 'POST',
          body: JSON.stringify({ height_cm, weight_series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error analyzing BMI trend:', error);
      throw error;
    }
  },

  vitalsSummary: async (series, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        return await fetchApi(API_ENDPOINTS.vitalsAnalytics + '/summary', {
          method: 'POST',
          body: JSON.stringify({ series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      } catch (enhancedError) {
        console.warn('Enhanced vitals endpoint failed, trying legacy:', enhancedError);
        return await fetchApi(`${API_BASE_URL}/analytics/vitals/summary`, {
          method: 'POST',
          body: JSON.stringify({ series }),
          token,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (error) {
      console.error('Error generating vitals summary:', error);
      throw error;
    }
  },
};
