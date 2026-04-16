import { useState } from 'react';
import ScanService from '../services/scanService';

// Custom hook for URL scanning
export function useScan() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scanResult, setScanResult] = useState(null);

  const analyzeUrl = async (url, token = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await ScanService.analyzeUrl(url, token);
      setScanResult(result);
      return { success: true, result };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  const clearResult = () => {
    setScanResult(null);
    setError(null);
  };

  return {
    loading,
    error,
    scanResult,
    analyzeUrl,
    clearResult,
  };
}
