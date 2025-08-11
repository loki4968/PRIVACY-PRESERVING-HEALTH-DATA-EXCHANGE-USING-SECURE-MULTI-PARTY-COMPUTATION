export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  register: `${API_BASE_URL}/register`,
  login: `${API_BASE_URL}/login`,
  uploads: `${API_BASE_URL}/uploads`,
  results: (id) => `${API_BASE_URL}/result/${id}`,
};

export const fetchApi = async (endpoint, options = {}) => {
  try {
    const headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      ...options.headers,
    };

    if (options.token) {
      headers.Authorization = `Bearer ${options.token}`;
    }

    const response = await fetch(endpoint, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Something went wrong');
    }

    return data;
  } catch (error) {
    if (error.message === 'Failed to fetch') {
      throw new Error('Network error - Please check if the backend server is running');
    }
    throw error;
  }
}; 