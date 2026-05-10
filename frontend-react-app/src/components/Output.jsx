import React from 'react';
import { ShieldCheck, Skull, Activity, AlertTriangle, CloudRain, Clock } from 'lucide-react';

function Output({ result, modelInfo }) {
  if (!result) {
    return (
      <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in relative z-10 text-center">
        <h2 className="text-3xl font-bold font-mono text-gray-400 mt-20">No Analysis Output</h2>
        <p className="text-gray-500 mt-4">Please go to the Scanner page and analyze a URL first.</p>
      </div>
    );
  }

  const isPhishing = result?.is_phishing;
  const themeColor = isPhishing ? 'text-neonRed' : 'text-neonBlue';
  const themeBorder = isPhishing ? 'border-neonRed glow-red' : 'border-neonBlue glow-blue';

  const renderHighlightedUrl = (urlStr) => {
    if (!isPhishing) return <span className="text-neonBlue">{urlStr}</span>;
    
    const keywords = [
      "login", "secure", "verify", "update", "bank", "account", 
      "signin", "auth", "confirm", "password", "ebay", "paypal", 
      "free", "lucky", "service", "bonus",
      "\\.tk", "\\.ml", "\\.ga", "\\.cf", "\\.gq", "\\.xyz", "\\.top", 
      "\\.club", "\\.online", "\\.site", "\\.icu", "\\.pw", "\\.cc", "\\.su"
    ];
    const ipPattern = "\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b";
    
    const regex = new RegExp(`(${keywords.join('|')}|${ipPattern})`, 'gi');
    const exactRegex = new RegExp(`^(${keywords.join('|')}|${ipPattern})$`, 'i');
    
    const parts = urlStr.split(regex);
    
    return (
      <span className="text-gray-400 break-all font-mono leading-loose">
        {parts.map((part, index) => {
          if (!part) return null;
          if (exactRegex.test(part)) {
            return (
              <span key={index} className="text-neonRed font-extrabold bg-red-900/40 px-1 py-0.5 mx-[1px] rounded border border-red-500/70 shadow-[0_0_10px_rgba(255,0,0,0.8)] animate-pulse" title="Phishing Indicator">
                {part}
              </span>
            );
          }
          return <span key={index} className="text-neonBlue">{part}</span>;
        })}
      </span>
    );
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 animate-fade-in relative z-10">
      <header className="text-center py-6">
        <h1 className="text-4xl md:text-5xl font-extrabold mb-3 tracking-tight font-mono">
          Analysis Output
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Detailed view of the scanned URL properties and threats.
        </p>
      </header>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in">
        {/* Prediction Card */}
        <div className={`glass rounded-2xl p-8 border ${themeBorder} flex flex-col items-center justify-center relative overflow-hidden`}>
          {isPhishing ? (
            <Skull className={`w-24 h-24 ${themeColor} mb-4`} />
          ) : (
            <ShieldCheck className={`w-24 h-24 ${themeColor} mb-4`} />
          )}
          <h2 className={`text-4xl font-bold uppercase tracking-widest ${themeColor} mb-2`}>
            {result.prediction}
          </h2>
          
          <div className="text-center font-mono text-sm break-all mt-4 mb-4 bg-gray-900/50 p-3 rounded-lg border border-gray-800 w-full">
            {renderHighlightedUrl(result.url)}
          </div>

          <div className="w-full mt-4 bg-gray-800 rounded-full h-4 overflow-hidden relative border border-gray-700">
            <div
              className={`h-full ${isPhishing ? 'bg-neonRed' : 'bg-neonBlue'} transition-all duration-1000 ease-out`}
              style={{ width: `${result.confidence_score}%` }}
            ></div>
          </div>
          <div className="flex justify-between w-full mt-2 font-mono text-sm text-gray-400">
            <span>Confidence Base</span>
            <span className="text-white">{result.confidence_score}%</span>
          </div>
        </div>

        {/* Details & SHAP Card */}
        <div className="glass rounded-2xl p-8 overflow-hidden border border-gray-800 flex flex-col space-y-6">
          
          {/* Intel Results */}
          {result.threat_intel && (
            <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
              <h3 className="text-lg font-bold mb-3 flex items-center text-gray-300">
                <CloudRain className="w-5 h-5 mr-2 text-neonBlue" /> Real-Time Threat Intel
              </h3>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-sm px-2 py-1 bg-gray-800 rounded">
                  {result.threat_intel.source}
                </span>
                {result.threat_intel.safe ? (
                  <span className="text-neonBlue text-sm font-bold flex items-center">
                     No signatures found
                  </span>
                ) : (
                  <span className="text-neonRed text-sm font-bold flex items-center">
                     <AlertTriangle className="w-4 h-4 mr-1" />
                     Matches Threat DB!
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Domain Security & Info */}
          {(result.domain_age_days !== undefined || result.sql_injection) && (
            <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
              <h3 className="text-lg font-bold mb-3 flex items-center text-gray-300">
                <ShieldCheck className="w-5 h-5 mr-2 text-neonBlue" /> Domain & Security Analysis
              </h3>
              <div className="space-y-4">
                {/* Domain Age */}
                {result.domain_age_days !== undefined && (
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-sm px-2 py-1 bg-gray-800 rounded min-w-[120px]">
                      Domain Age
                    </span>
                    {result.domain_age_days === null ? (
                      <span className="text-gray-400 text-sm font-bold flex items-center">
                         Unknown or hidden
                      </span>
                    ) : result.domain_age_days < 30 ? (
                      <span className="text-neonRed text-sm font-bold flex items-center">
                         <AlertTriangle className="w-4 h-4 mr-1" />
                         Very Young ({result.domain_age_days} days)
                      </span>
                    ) : result.domain_age_days < 180 ? (
                       <span className="text-yellow-500 text-sm font-bold flex items-center">
                         <AlertTriangle className="w-4 h-4 mr-1" />
                         Recent ({result.domain_age_days} days)
                       </span>
                    ) : (
                      <span className="text-neonBlue text-sm font-bold flex items-center">
                         Established ({Math.round(result.domain_age_days / 365.25 * 10) / 10} years)
                      </span>
                    )}
                  </div>
                )}

                {/* SQL Injection Analysis */}
                {result.sql_injection && (
                  <div className="flex flex-col space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm px-2 py-1 bg-gray-800 rounded min-w-[120px]">
                        SQL Injection
                      </span>
                      <span className="text-gray-300 text-sm">
                        {result.sql_injection.details}
                      </span>
                      {result.sql_injection.detected ? (
                        <span className="text-neonRed text-sm font-bold flex items-center ml-auto">
                           <AlertTriangle className="w-4 h-4 mr-1" />
                           Detected
                        </span>
                      ) : (
                        <span className="text-neonBlue text-sm font-bold flex items-center ml-auto">
                           Clean
                        </span>
                      )}
                    </div>
                    {result.sql_injection.detected && (
                      <div className="mt-1 text-sm font-mono text-neonRed ml-[128px]">
                        Matches: {result.sql_injection.matches.join(', ')}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* SHAP Values */}
          <div>
            <h3 className="text-xl font-bold mb-4 flex items-center border-b border-gray-700 pb-2">
              <Activity className="w-5 h-5 mr-2 text-neonBlue" />
              Suspicious Indicators (SHAP)
            </h3>
            {result.top_suspicious.length === 0 ? (
              <div className="text-gray-400 p-4 text-center">No strong phishing indicators found.</div>
            ) : (
              <div className="space-y-3 mt-4">
                {result.top_suspicious.map((feat, i) => (
                  <div key={i} className="flex justify-between items-center bg-gray-800/50 p-3 rounded-lg border border-gray-700 hover:border-neonRed transition-colors">
                    <div className="font-mono">
                      <span className="text-gray-300">{feat.feature.replace(/_/g, ' ')}</span>
                      <span className="text-xs text-neonBlue ml-2 bg-blue-900/30 px-2 py-1 rounded">Val: {feat.value}</span>
                    </div>
                    <div className="text-neonRed font-bold">
                      +{feat.shap_value.toFixed(3)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Model Performance */}
      {modelInfo && (
        <div className="glass rounded-2xl p-8 mt-12 border border-blue-900/30">
          <h3 className="text-2xl font-bold mb-6 font-mono text-center text-gray-300">Ensemble Architecture Performance</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono">
              <thead className="text-neonBlue border-b border-gray-700">
                <tr>
                  <th className="p-4">Model</th>
                  <th className="p-4">Accuracy</th>
                  <th className="p-4">Precision</th>
                  <th className="p-4 bg-blue-900/10 rounded-t-lg border-b-2 border-neonBlue">Recall 🎯</th>
                  <th className="p-4">F1 Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 text-gray-300">
                {Object.entries(modelInfo.metrics).map(([name, m]) => (
                  <tr key={name} className={name === 'ENSEMBLE' ? 'bg-blue-900/20 font-bold text-white' : 'hover:bg-gray-800/30'}>
                    <td className="p-4">{name}</td>
                    <td className="p-4">{(m.accuracy * 100).toFixed(1)}%</td>
                    <td className="p-4">{(m.precision * 100).toFixed(1)}%</td>
                    <td className="p-4 text-neonBlue bg-blue-900/10">{(m.recall * 100).toFixed(1)}%</td>
                    <td className="p-4">{(m.f1 * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default Output;
