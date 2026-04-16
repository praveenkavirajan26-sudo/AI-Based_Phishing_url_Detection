import React, { useState } from 'react';
import { ShieldAlert, LogOut, User, LayoutDashboard, Search, PieChart } from 'lucide-react';
import Scanner from './components/Scanner';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';
import Output from './components/Output';
import { Alert } from './components/ui/Common';

function App() {
  const [currentView, setCurrentView] = useState('scanner');
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [username, setUsername] = useState(localStorage.getItem('username') || null);
  const [scanResult, setScanResult] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername(null);
    setCurrentView('auth');
  };

  // If user is logged in, redirect to scanner
  React.useEffect(() => {
    if (token && currentView === 'auth') {
      setCurrentView('scanner');
    }
  }, [token, currentView]);

  return (
    <div className="min-h-screen bg-black text-white font-sans flex flex-col relative overflow-hidden">
      {/* Background gradients */}
      <div className="fixed -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-neonBlue opacity-5 blur-[120px] pointer-events-none"></div>
      <div className="fixed top-[60%] -right-[10%] w-[50%] h-[50%] rounded-full bg-neonRed opacity-5 blur-[120px] pointer-events-none"></div>

      {/* Navbar */}
      <nav className="border-b border-gray-800 bg-black/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2 cursor-pointer group" onClick={() => setCurrentView('scanner')}>
            <ShieldAlert className="w-8 h-8 text-neonBlue group-hover:pulse" />
            <span className="text-xl font-bold font-mono tracking-widest hidden sm:block">PHISH<span className="text-neonBlue">GUARD</span></span>
          </div>
          
          <div className="flex items-center space-x-2 sm:space-x-4">
            <button 
              onClick={() => setCurrentView('scanner')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors font-mono tracking-wide ${currentView === 'scanner' ? 'bg-gray-800 text-neonBlue' : 'text-gray-400 hover:text-white'}`}
            >
              <Search className="w-5 h-5" />
              <span className="hidden sm:inline">Scanner</span>
            </button>

            <button 
              onClick={() => setCurrentView('output')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors font-mono tracking-wide ${currentView === 'output' ? 'bg-gray-800 text-neonBlue' : 'text-gray-400 hover:text-white'}`}
            >
              <PieChart className="w-5 h-5" />
              <span className="hidden sm:inline">Output</span>
            </button>
            
            {token ? (
              <>
                <button 
                  onClick={() => setCurrentView('dashboard')}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors font-mono tracking-wide ${currentView === 'dashboard' ? 'bg-gray-800 text-neonBlue' : 'text-gray-400 hover:text-white'}`}
                >
                  <LayoutDashboard className="w-5 h-5" />
                  <span className="hidden sm:inline">History</span>
                </button>
                <div className="flex items-center space-x-2 px-3 py-2 text-neonBlue font-mono text-sm">
                  <User className="w-4 h-4" />
                  <span className="hidden sm:inline">{username || 'User'}</span>
                </div>
                <button 
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-3 py-2 text-red-500 hover:bg-red-900/40 rounded-lg transition-colors font-mono"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </>
            ) : (
              <button 
                onClick={() => setCurrentView('auth')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-bold tracking-wider uppercase text-sm ${currentView === 'auth' ? 'bg-neonBlue text-black shadow-[0_0_15px_rgba(0,255,255,0.4)]' : 'bg-gray-800 text-white hover:bg-gray-700'}`}
              >
                <User className="w-4 h-4" />
                <span>Portal</span>
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center">
        {!token && currentView === 'scanner' && (
          // Landing page for non-logged users
          <div className="w-full max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in relative z-10 text-center mt-20">
            <div className="mb-8">
              <ShieldAlert className="w-24 h-24 text-neonBlue mx-auto mb-6 animate-pulse" />
              <h1 className="text-5xl md:text-6xl font-extrabold font-mono mb-4">
                PHISH<span className="text-neonBlue">GUARD</span> AI
              </h1>
              <p className="text-xl text-gray-400 mb-2">Advanced Phishing Detection System</p>
              <p className="text-sm text-gray-500">Powered by Ensemble Machine Learning</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              <div className="glass p-6 rounded-xl">
                <div className="text-neonBlue text-4xl mb-3">🤖</div>
                <h3 className="font-bold text-lg mb-2">AI-Powered</h3>
                <p className="text-sm text-gray-400">Random Forest + XGBoost + LightGBM ensemble model</p>
              </div>
              <div className="glass p-6 rounded-xl">
                <div className="text-neonBlue text-4xl mb-3"></div>
                <h3 className="font-bold text-lg mb-2">25 Features</h3>
                <p className="text-sm text-gray-400">Comprehensive URL analysis with SHAP explainability</p>
              </div>
              <div className="glass p-6 rounded-xl">
                <div className="text-neonBlue text-4xl mb-3">⚡</div>
                <h3 className="font-bold text-lg mb-2">Real-Time</h3>
                <p className="text-sm text-gray-400">Instant threat detection with Google Safe Browsing</p>
              </div>
            </div>

            <div className="glass p-8 rounded-2xl border border-neonBlue/30">
              <h2 className="text-2xl font-bold font-mono mb-4">Get Started</h2>
              <p className="text-gray-400 mb-6">Create a free account to unlock all features</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => setCurrentView('auth')}
                  className="bg-neonBlue text-black font-bold px-8 py-3 rounded-xl hover:bg-white transition-all"
                >
                  Create Free Account
                </button>
                <button
                  onClick={() => setCurrentView('scanner')}
                  className="bg-gray-800 text-white font-bold px-8 py-3 rounded-xl hover:bg-gray-700 transition-all"
                >
                  Try Without Account
                </button>
              </div>
            </div>

            <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="text-gray-500">
                <div className="text-neonBlue font-bold text-2xl mb-1">95%+</div>
                <div>Accuracy Rate</div>
              </div>
              <div className="text-gray-500">
                <div className="text-neonBlue font-bold text-2xl mb-1">&lt;1s</div>
                <div>Avg. Scan Time</div>
              </div>
              <div className="text-gray-500">
                <div className="text-neonBlue font-bold text-2xl mb-1">10K+</div>
                <div>URLs Analyzed</div>
              </div>
              <div className="text-gray-500">
                <div className="text-neonBlue font-bold text-2xl mb-1">24/7</div>
                <div>Protection</div>
              </div>
            </div>
          </div>
        )}

        {token && currentView === 'scanner' && (
           <Scanner token={token} onResult={(res, info) => {
             setScanResult(res);
             setModelInfo(info);
             setCurrentView('output');
           }} />
        )}
        
        {currentView === 'output' && (
          token ? (
            <Output result={scanResult} modelInfo={modelInfo} />
          ) : (
            <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in relative z-10 text-center mt-20">
              <Alert message="Please login to view analysis results" type="warning" />
              <button
                onClick={() => setCurrentView('auth')}
                className="mt-4 bg-neonBlue text-black font-bold px-6 py-2 rounded-xl hover:bg-white transition-all"
              >
                Login to Continue
              </button>
            </div>
          )
        )}
        
        {currentView === 'auth' && <Auth setToken={setToken} setCurrentView={setCurrentView} setUsername={setUsername} />}
        
        {currentView === 'dashboard' && (
          token ? (
            <Dashboard token={token} />
          ) : (
            <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in relative z-10">
              <Alert message="Please login to view your scan history" type="warning" />
            </div>
          )
        )}
      </main>
    </div>
  );
}

export default App;
