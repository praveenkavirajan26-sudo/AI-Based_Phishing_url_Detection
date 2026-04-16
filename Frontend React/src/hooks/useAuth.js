import { useState, useEffect } from 'react';
import AuthService from '../services/authService';

// Custom hook for authentication
export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(AuthService.isAuthenticated());
  const [username, setUsername] = useState(AuthService.getUsername());
  const [token, setToken] = useState(AuthService.getToken());

  useEffect(() => {
    // Listen for storage changes (logout in another tab)
    const handleStorageChange = () => {
      setIsAuthenticated(AuthService.isAuthenticated());
      setUsername(AuthService.getUsername());
      setToken(AuthService.getToken());
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = async (username, password) => {
    try {
      const data = await AuthService.login(username, password);
      AuthService.saveAuthData(data.access_token, username);
      setToken(data.access_token);
      setUsername(username);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const register = async (username, password) => {
    try {
      await AuthService.register(username, password);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    AuthService.logout();
    setToken(null);
    setUsername(null);
    setIsAuthenticated(false);
  };

  return {
    isAuthenticated,
    username,
    token,
    login,
    register,
    logout,
  };
}
