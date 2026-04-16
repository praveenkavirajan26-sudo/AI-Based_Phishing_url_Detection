// Scan Service
import { API_ENDPOINTS, apiRequest } from '../config/api';

class ScanService {
  // Analyze URL for phishing
  static async analyzeUrl(url, token = null) {
    return await apiRequest(API_ENDPOINTS.predict, {
      method: 'POST',
      body: { url },
      token,
    });
  }

  // Get user scan history
  static async getHistory(token) {
    if (!token) {
      throw new Error('Authentication required');
    }
    
    return await apiRequest(API_ENDPOINTS.history, {
      method: 'GET',
      token,
    });
  }

  // Get model information
  static async getModelInfo() {
    return await apiRequest(API_ENDPOINTS.modelInfo, {
      method: 'GET',
    });
  }

  // Check API health
  static async checkHealth() {
    return await apiRequest(API_ENDPOINTS.health, {
      method: 'GET',
    });
  }
}

export default ScanService;
