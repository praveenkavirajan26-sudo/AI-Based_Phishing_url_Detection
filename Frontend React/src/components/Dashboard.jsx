import React from 'react';
import { Activity, Calendar, ShieldCheck, Skull, Link as LinkIcon, TrendingUp, AlertTriangle, Shield } from 'lucide-react';
import { useScanHistory } from '../hooks/useScanHistory';
import { LoadingSpinner, Alert, Card } from './ui/Common';
import { formatDate } from '../utils/helpers';

function Dashboard({ token }) {
  const { history, loading, error, refreshHistory } = useScanHistory(token);

  // Calculate statistics
  const totalScans = history.length;
  const phishingDetected = history.filter(h => h.prediction === 'Phishing').length;
  const safeUrls = history.filter(h => h.prediction === 'Legitimate').length;
  const avgRiskScore = totalScans > 0 
    ? (history.reduce((sum, h) => sum + h.risk_score, 0) / totalScans).toFixed(1)
    : 0;

  if (!token) {
    return (
      <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in relative z-10">
        <Alert 
          type="warning" 
          message="Please login to view your scan history and dashboard." 
        />
      </div>
    );
  }

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading scan history..." />;
  }

  if (error) {
    return <Alert type="error" message={error} />;
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in relative z-10 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="w-8 h-8 text-neonBlue" />
          <h2 className="text-3xl font-bold font-mono text-neonBlue tracking-widest">THREAT INTEL DASHBOARD</h2>
        </div>
        <button 
          onClick={refreshHistory}
          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-mono transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="flex items-center space-x-4">
          <div className="p-3 bg-blue-900/30 rounded-lg">
            <TrendingUp className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Total Scans</p>
            <p className="text-2xl font-bold font-mono">{totalScans}</p>
          </div>
        </Card>

        <Card className="flex items-center space-x-4">
          <div className="p-3 bg-red-900/30 rounded-lg">
            <Skull className="w-6 h-6 text-red-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Phishing Found</p>
            <p className="text-2xl font-bold font-mono text-red-400">{phishingDetected}</p>
          </div>
        </Card>

        <Card className="flex items-center space-x-4">
          <div className="p-3 bg-green-900/30 rounded-lg">
            <Shield className="w-6 h-6 text-green-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Safe URLs</p>
            <p className="text-2xl font-bold font-mono text-green-400">{safeUrls}</p>
          </div>
        </Card>

        <Card className="flex items-center space-x-4">
          <div className="p-3 bg-yellow-900/30 rounded-lg">
            <AlertTriangle className="w-6 h-6 text-yellow-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Avg Risk Score</p>
            <p className="text-2xl font-bold font-mono text-yellow-400">{avgRiskScore}%</p>
          </div>
        </Card>
      </div>

      {/* History Table */}
      {history.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg mb-2">No scanning history found</p>
            <p className="text-gray-500 text-sm">Start scanning URLs to see your history here</p>
          </div>
        </Card>
      ) : (
        <Card className="overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left font-sans">
              <thead className="bg-gray-900/80 text-gray-300 uppercase text-xs tracking-wider border-b border-gray-800">
                <tr>
                  <th className="p-4 rounded-tl-2xl">#</th>
                  <th className="p-4">URL</th>
                  <th className="p-4">Prediction</th>
                  <th className="p-4">Risk Score</th>
                  <th className="p-4">Confidence</th>
                  <th className="p-4 rounded-tr-2xl">Scanned At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50">
                {history.map((scan, index) => {
                  const isPhish = scan.prediction === "Phishing";
                  return (
                    <tr key={scan.id} className="hover:bg-gray-800/40 transition-colors">
                      <td className="p-4 font-mono text-sm text-gray-500">{index + 1}</td>
                      <td className="p-4 font-mono text-sm max-w-xs truncate text-gray-200">
                        <div className="flex items-center space-x-2">
                          <LinkIcon className="w-4 h-4 text-gray-500 flex-shrink-0" />
                          <span className="truncate" title={scan.url}>{scan.url}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className={`flex items-center space-x-2 font-bold ${isPhish ? 'text-neonRed' : 'text-neonBlue'}`}>
                          {isPhish ? <Skull className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                          <span>{scan.prediction}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-20 h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full transition-all ${isPhish ? 'bg-neonRed' : 'bg-neonBlue'}`} 
                              style={{width: `${scan.risk_score}%`}}
                            ></div>
                          </div>
                          <span className={`font-mono text-sm font-bold ${isPhish ? 'text-neonRed' : 'text-neonBlue'}`}>
                            {scan.risk_score}%
                          </span>
                        </div>
                      </td>
                      <td className="p-4 font-mono text-sm text-gray-400">
                        {scan.confidence_score}%
                      </td>
                      <td className="p-4 text-sm text-gray-500 font-mono">
                        {formatDate(scan.timestamp)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

export default Dashboard;

