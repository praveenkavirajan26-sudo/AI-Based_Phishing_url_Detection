import React, { useState, useEffect } from 'react';
import { ShieldAlert, Link as LinkIcon, Cpu, ShieldCheck, Skull, Activity, AlertTriangle, CloudRain, Clock } from 'lucide-react';

const API_URL = "http://localhost:8000";

function Scanner({ token, onResult }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/model-info`)
      .then(res => res.json())
      .then(data => setModelInfo(data))
      .catch(err => console.error("Could not load model info", err));
  }, []);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setError('');
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ url })
      });
      if (!res.ok) throw new Error("API Error");
      const data = await res.json();
      
      // Pass the fully computed results up to the parent App
      if (onResult) {
        onResult(data, modelInfo);
      }
    } catch (err) {
      setError('Failed to analyze URL. Is the backend running?');
    }
    setLoading(false);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 animate-fade-in relative z-10">
      <header className="text-center py-6 mt-16">
        <h1 className="text-4xl md:text-5xl font-extrabold mb-3 tracking-tight font-mono flex justify-center items-center">
          <ShieldAlert className="w-10 h-10 mr-3 text-neonBlue pb-1" />
          AI Phishing Scanner
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Driven by Ensemble Learning and SHAP explainability.
        </p>
      </header>

      <form onSubmit={handleAnalyze} className="max-w-3xl mx-auto w-full relative group">
        <div className={`glass rounded-2xl p-2 flex items-center transition-all duration-300 ${url ? 'glow-blue border-neonBlue' : 'border-gray-800'}`}>
          <LinkIcon className={`ml-4 w-6 h-6 ${url ? 'text-neonBlue' : 'text-gray-400'}`} />
          <input
            type="text"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://example.com/login"
            className="w-full bg-transparent border-none text-xl p-4 focus:ring-0 focus:outline-none text-white font-mono placeholder-gray-600"
          />
          <button
            disabled={loading || !url}
            type="submit"
            className="bg-neonBlue text-black font-bold px-8 py-4 rounded-xl hover:bg-white transition-all disabled:opacity-50 min-w-[140px] uppercase tracking-wider relative overflow-hidden"
          >
            {loading ? <span className="pulse">Scanning...</span> : "Analyze"}
          </button>
        </div>
      </form>

      {error && (
        <div className="text-center font-mono p-4 glass rounded-xl border-red-900 border max-w-lg mx-auto flex items-center justify-center text-neonRed">
          <AlertTriangle className="mr-2" /> {error}
        </div>
      )}

      {loading && (
        <div className="max-w-3xl mx-auto h-64 glass rounded-2xl relative overflow-hidden flex flex-col items-center justify-center border border-neonBlue border-opacity-30">
          <div className="scan-line"></div>
          <Cpu className="w-16 h-16 text-neonBlue pulse mb-4" />
          <p className="font-mono text-neonBlue text-xl">Extracting 20+ Features...</p>
        </div>
      )}
    </div>
  );
}

export default Scanner;
