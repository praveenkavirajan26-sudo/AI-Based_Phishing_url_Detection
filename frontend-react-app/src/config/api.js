// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// API Endpoints
export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  register: `${API_BASE_URL}/register`,
  login: `${API_BASE_URL}/login`,
  predict: `${API_BASE_URL}/predict`,
  history: `${API_BASE_URL}/history`,
  modelInfo: `${API_BASE_URL}/model-info`,
  profile: `${API_BASE_URL}/user/profile`,
};

// Request headers helper
export const getHeaders = (token = null, contentType = 'application/json') => {
  const headers = {
    'Content-Type': contentType,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// API request helper
const getErrorMessage = (data, status) => {
  const detail = data?.detail ?? data?.message ?? data?.error;

  if (typeof detail === 'string') {
    return detail;
  }

  if (detail && typeof detail === 'object') {
    if (detail.message) {
      return detail.message;
    }

    if (detail.error) {
      return detail.error;
    }

    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg || item.message || String(item)).join(', ');
    }
  }

  return `API Error: ${status}`;
};

export const apiRequest = async (endpoint, options = {}) => {
  const { token, method = 'GET', body, contentType } = options;
  
  const config = {
    method,
    headers: getHeaders(token, contentType),
  };
  
  if (body) {
    config.body = contentType === 'application/x-www-form-urlencoded' 
      ? body 
      : JSON.stringify(body);
  }
  
  try {
    const response = await fetch(endpoint, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(getErrorMessage(data, response.status));
    }
    
    return data;
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
};
