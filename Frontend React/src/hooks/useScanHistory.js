import { useState, useEffect } from 'react';
import ScanService from '../services/scanService';

// Custom hook for scan history
export function useScanHistory(token) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await ScanService.getHistory(token);
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [token]);

  const refreshHistory = () => {
    fetchHistory();
  };

  return {
    history,
    loading,
    error,
    refreshHistory,
  };
}
