// Authentication Service
import { API_ENDPOINTS, apiRequest } from '../config/api';

class AuthService {
  // Register new user
  static async register(username, password, email) {
    const body = { username, password };
    if (email) {
      body.email = email;
    }
    
    return await apiRequest(API_ENDPOINTS.register, {
      method: 'POST',
      body: body,
    });
  }

  // Login user
  static async login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    return await apiRequest(API_ENDPOINTS.login, {
      method: 'POST',
      body: formData,
      contentType: 'application/x-www-form-urlencoded',
    });
  }

  // Save auth data to localStorage
  static saveAuthData(token, username) {
    localStorage.setItem('token', token);
    localStorage.setItem('username', username);
  }

  // Get current user token
  static getToken() {
    return localStorage.getItem('token');
  }

  // Get current username
  static getUsername() {
    return localStorage.getItem('username');
  }

  // Check if user is authenticated
  static isAuthenticated() {
    return !!localStorage.getItem('token');
  }

  // Logout user
  static logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  }
}

export default AuthService;
