import { API_BASE_URL, fetchApi } from '../config/api';
import { API_ENDPOINTS } from '../config/api';

// Use the API_ENDPOINTS for consistent endpoint management

export const secureComputationService = {
  /**
   * Get pending computation requests for the current user
   * @param {string} token - Authentication token
   * @returns {Promise<Array<Object>>} - List of pending computation requests
   */
  getPendingRequests: async (token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        const response = await fetchApi(API_ENDPOINTS.enhancedSecureComputations + '/pending-requests', {
          method: 'GET',
          token,
        });
        return response;
      } catch (enhancedError) {
        console.warn('Enhanced endpoint failed, trying legacy endpoint:', enhancedError);
        const response = await fetchApi(API_ENDPOINTS.pendingComputationRequests, {
          method: 'GET',
          token,
        });
        return response;
      }
    } catch (error) {
      console.error('Error getting pending computation requests:', error);
      throw error;
    }
  },

  /**
   * Submit CSV to a computation with optional column mapping
   * @param {string} computationId
   * @param {File|Blob} file - CSV file
   * @param {Object} options - Optional mapping
   * @param {boolean} [options.has_header=true]
   * @param {string} [options.delimiter=","]
   * @param {string} [options.column] - Single header name
   * @param {string} [options.columns] - Comma-separated header names (or indices if has_header=false)
   * @param {number} [options.column_index] - Single column index when has_header=false
   * @param {string} token
   */
  submitCsv: async (computationId, file, options = {}, token) => {
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('description', options.description || 'CSV upload');
      form.append('security_method', options.security_method || 'standard');
      if (typeof options.has_header !== 'undefined') {
        form.append('has_header', String(!!options.has_header));
      } else {
        form.append('has_header', 'true');
      }
      if (options.delimiter) form.append('delimiter', options.delimiter);
      if (options.column) form.append('column', options.column);
      if (options.columns) form.append('columns', options.columns);
      if (typeof options.column_index !== 'undefined' && options.column_index !== null) {
        form.append('column_index', String(options.column_index));
      }

      // Use direct fetch since fetchApi auto-sets Content-Type; we need FormData boundary
      const endpoint = API_ENDPOINTS.submitData(computationId).replace('/submit', '/submit-csv');
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: form,
      });
      const contentType = res.headers.get('content-type') || '';
      const json = contentType.includes('application/json') ? await res.json() : await res.text();
      if (!res.ok) {
        const message = (json && json.detail) ? json.detail : `CSV upload failed (${res.status})`;
        const err = new Error(message);
        err.status = res.status;
        throw err;
      }
      return json;
    } catch (error) {
      console.error(`Error submitting CSV to computation ${computationId}:`, error);
      throw error;
    }
  },
  
  /**
   * Get user's submission for a specific computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - User's submission data
   */
  getUserSubmission: async (computationId, token) => {
    try {
      // Try multiple endpoints to find user submission
      let response;
      
      try {
        // First try the mySubmission endpoint
        response = await fetchApi(API_ENDPOINTS.mySubmission(computationId), {
          method: 'GET',
          token,
        });
      } catch (firstError) {
        if (firstError.status === 404) {
          // Try the userSubmission endpoint as fallback
          try {
            response = await fetchApi(API_ENDPOINTS.userSubmission(computationId), {
              method: 'GET',
              token,
            });
          } catch (secondError) {
            if (secondError.status === 404) {
              return { has_submitted: false, message: 'No submission found' };
            }
            throw secondError;
          }
        } else {
          throw firstError;
        }
      }
      
      return response;
    } catch (error) {
      console.error(`Error getting user submission for computation ${computationId}:`, error);
      // If 404, return null instead of throwing
      if (error.status === 404) {
        return { has_submitted: false, message: 'No submission found' };
      }
      throw error;
    }
  },
  
  /**
   * Get available organizations for secure computations
   * @param {string} token - Authentication token
   * @returns {Promise<Array<Object>>} - List of available organizations
   */
  getAvailableOrganizations: async (token) => {
    try {
      const response = await fetchApi(`${API_BASE_URL}/secure-computations/organizations`, {
        method: 'GET',
        token,
      });
      return response;
    } catch (error) {
      console.error('Error getting available organizations:', error);
      throw error;
    }
  },

  /**
   * Get active participants for a computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Array<Object>>} - List of active participants
   */
  getActiveParticipants: async (computationId, token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.activeParticipants(computationId), {
        method: 'GET',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error getting participants for computation ${computationId}:`, error);
      throw error;
    }
  },
  
  /**
   * Get details for a specific computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Computation details
   */
  getComputationDetails: async (computationId, token) => {
    try {
      // Try the secure computations endpoint first
      const response = await fetchApi(API_ENDPOINTS.computationDetails(computationId), {
        method: 'GET',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error getting details for computation ${computationId}:`, error);
      // If that fails, try the result endpoint as fallback
      try {
        const fallbackResponse = await fetchApi(API_ENDPOINTS.computationResult(computationId), {
          method: 'GET',
          token,
        });
        return fallbackResponse;
      } catch (fallbackError) {
        console.error(`Fallback also failed:`, fallbackError);
        throw error; // Throw original error
      }
    }
  },
  /**
   * Create a new secure computation
   * @param {Object} params - Computation parameters
   * @param {string} params.computation_type - Type of computation
   * @param {Array<string>} params.participating_orgs - List of participating organization IDs
   * @param {string} params.security_method - Security method (standard, homomorphic, hybrid)
   * @param {number} params.threshold - Threshold for SMPC (only used with hybrid security method)
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Created computation details
   */
  createComputation: async (params, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        const response = await fetchApi(API_ENDPOINTS.createEnhancedComputation, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(params),
          token,
        });
        return response;
      } catch (enhancedError) {
        console.warn('Enhanced endpoint failed, trying legacy endpoint:', enhancedError);
        const response = await fetchApi(API_ENDPOINTS.createComputation, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(params),
          token,
        });
        return response;
      }
    } catch (error) {
      console.error('Error creating computation:', error);
      throw error;
    }
  },
  
  /**
   * Create a new computation request to other organizations
   * @param {Object} params - Request parameters
   * @param {string} params.title - Title of the computation
   * @param {string} params.description - Description of the computation
   * @param {string} params.computation_type - Type of computation
   * @param {Array<string>} params.target_organizations - List of target organization IDs
   * @param {string} params.security_method - Security method (standard, homomorphic, hybrid)
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Created request details
   */
  createComputationRequest: async (params, token) => {
    try {
      const response = await fetchApi(`${API_BASE_URL}/secure-computations/requests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
        token,
      });
      return response;
    } catch (error) {
      console.error('Error creating computation request:', error);
      throw error;
    }
  },
  
  /**
   * Initialize a new computation or send computation requests to other organizations
   * @param {Object} params - Computation parameters
   * @param {string} params.computation_type - Type of computation
   * @param {Array<string>} params.participating_orgs - List of participating organization IDs
   * @param {string} params.security_method - Security method (standard, homomorphic, hybrid)
   * @param {string} params.title - Title of the computation (for requests)
   * @param {string} params.description - Description of the computation (for requests)
   * @param {Array<string>} params.target_organizations - List of target organization IDs (for requests)
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Created computation details
   */
  initializeComputation: async (params, token) => {
    try {
      // If target_organizations is provided, create a computation request to other organizations
      if (params.target_organizations && params.target_organizations.length > 0) {
        return await secureComputationService.createComputationRequest({
          title: params.title || 'Secure Computation Request',
          description: params.description || 'Please join this secure computation',
          computation_type: params.computation_type || 'health_statistics',
          target_organizations: params.target_organizations,
          security_method: params.security_method || 'standard'
        }, token);
      } 
      // Otherwise, create a new computation for the current organization
      else {
        return await secureComputationService.createComputation({
          computation_type: params.computation_type || 'health_statistics',
          participating_orgs: params.participating_orgs || [],
          security_method: params.security_method || 'standard'
        }, token);
      }
    } catch (error) {
      console.error('Error initializing computation:', error);
      throw error;
    }
  },

  /**
   * Get a list of all computations
   * @param {string} token - Authentication token
   * @returns {Promise<Array<Object>>} - List of computations
   */
  listComputations: async (token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.secureComputations, {
        method: 'GET',
        token,
      });
      return response;
    } catch (error) {
      console.error('Error listing computations:', error);
      throw error;
    }
  },

  /**
   * Get details of a specific computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Computation details
   */
  getComputation: async (computationId, token) => {
    try {
      // Backend exposes result/details at /computations/{id}/result
      const response = await fetchApi(`${API_ENDPOINTS.secureComputationById(computationId)}/result`, {
        method: 'GET',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error getting computation ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Get computation result for a specific computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Computation result
   */
  getComputationResult: async (computationId, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        const response = await fetchApi(API_ENDPOINTS.getEnhancedResult(computationId), {
          method: 'GET',
          token,
        });
        return response;
      } catch (enhancedError) {
        console.warn('Enhanced endpoint failed, trying legacy endpoint:', enhancedError);
        const response = await fetchApi(API_ENDPOINTS.computationResult(computationId), {
          method: 'GET',
          token,
        });
        return response;
      }
    } catch (error) {
      console.error(`Error getting computation result ${computationId}:`, error);
      throw error;
    }
  },
  

  /**
   * Join an existing computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Join result
   */
  joinComputation: async (computationId, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        const response = await fetchApi(API_ENDPOINTS.joinEnhancedComputation(computationId), {
          method: 'POST',
          token,
        });
        return response;
      } catch (enhancedError) {
        console.warn('Enhanced endpoint failed, trying legacy endpoint:', enhancedError);
        const response = await fetchApi(API_ENDPOINTS.joinComputation(computationId), {
          method: 'POST',
          token,
        });
        return response;
      }
    } catch (error) {
      console.error(`Error joining computation ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Accept a computation request
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Accept result
   */
  acceptComputationRequest: async (computationId, token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.acceptComputationRequest(computationId), {
        method: 'POST',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error accepting computation request ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Decline a computation request
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Decline result
   */
  declineComputationRequest: async (computationId, token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.declineComputationRequest(computationId), {
        method: 'POST',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error declining computation request ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Submit data to a computation
   * @param {string} computationId - Computation ID
   * @param {Object} data - Data submission
   * @param {number|Array<number>} data.value - Data value(s) to submit
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Submission result
   */
  submitData: async (computationId, data, token) => {
    try {
      // Try enhanced endpoint first, fallback to legacy
      try {
        const response = await fetchApi(API_ENDPOINTS.submitEnhancedData(computationId), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
          token,
        });
        return response;
      } catch (enhancedError) {
        console.warn('Enhanced endpoint failed, trying legacy endpoint:', enhancedError);
        const response = await fetchApi(API_ENDPOINTS.submitData(computationId), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
          token,
        });
        return response;
      }
    } catch (error) {
      console.error(`Error submitting data to computation ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Perform computation on submitted data
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Computation result
   */
  performComputation: async (computationId, token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.performComputation(computationId), {
        method: 'POST',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error performing computation ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Export computation results
   * @param {string} computationId - Computation ID
   * @param {Object} params - Export parameters
   * @param {string} params.format - Export format (json, csv)
   * @param {boolean} params.include_sensitive_data - Whether to include sensitive data
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Export result
   */
  exportResults: async (computationId, params, token) => {
    try {
      // Use a direct fetch here to handle binary responses (CSV/JSON download)
      const url = API_ENDPOINTS.exportResults(computationId) + (params?.format ? `?format=${encodeURIComponent(params.format)}` : '');
      const res = await fetch(url, {
        method: 'GET',
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          Accept: '*/*',
        },
      });

      if (!res.ok) {
        // Try to parse JSON error if available
        let detail = 'Failed to export results';
        try {
          const data = await res.json();
          detail = data?.detail || detail;
        } catch (_) {}
        throw new Error(detail);
      }

      const blob = await res.blob();
      const disposition = res.headers.get('Content-Disposition') || '';
      const match = /filename="?([^";]+)"?/i.exec(disposition);
      const filename = match ? match[1] : `computation_${computationId}.${params?.format === 'csv' ? 'csv' : 'json'}`;

      return { blob, filename };
    } catch (error) {
      console.error(`Error exporting results for computation ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Delete result
   */
  deleteComputation: async (computationId, token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.deleteComputation(computationId), {
        method: 'DELETE',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error deleting computation ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Invite a participant to an existing computation
   * @param {string} computationId - Computation ID
   * @param {number} orgId - Organization ID to invite
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Invitation result
   */
  inviteParticipant: async (computationId, orgId, token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.inviteParticipant(computationId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ org_id: orgId }),
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error inviting participant to computation ${computationId}:`, error);
      throw error;
    }
  },

  /**
   * Delete user's submission for a specific computation
   * @param {string} computationId - Computation ID
   * @param {string} token - Authentication token
   * @returns {Promise<Object>} - Delete result
   */
  deleteSubmission: async (computationId, token) => {
    try {
      const response = await fetchApi(API_ENDPOINTS.deleteSubmission(computationId), {
        method: 'DELETE',
        token,
      });
      return response;
    } catch (error) {
      console.error(`Error deleting submission for computation ${computationId}:`, error);
      throw error;
    }
  }
};