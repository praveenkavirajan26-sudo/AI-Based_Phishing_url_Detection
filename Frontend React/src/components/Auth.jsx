import React, { useState } from 'react';
import { User, Lock, Mail, ArrowRight, UserPlus, Shield, Eye, EyeOff, CheckCircle, XCircle } from 'lucide-react';
import { Alert, Button, Input } from './ui/Common';
import AuthService from '../services/authService';

function Auth({ setToken, setCurrentView, setUsername: setParentUsername }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Password strength checker
  const getPasswordStrength = (pwd) => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (pwd.length >= 12) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[a-z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;
    
    if (strength <= 2) return { level: 'Weak', color: 'text-red-400', bg: 'bg-red-400' };
    if (strength <= 4) return { level: 'Medium', color: 'text-yellow-400', bg: 'bg-yellow-400' };
    return { level: 'Strong', color: 'text-green-400', bg: 'bg-green-400' };
  };

  const passwordStrength = getPasswordStrength(password);

  // Password validation
  const validatePassword = (pwd) => {
    const errors = [];
    if (pwd.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(pwd)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(pwd)) errors.push('One lowercase letter');
    if (!/[0-9]/.test(pwd)) errors.push('One number');
    return errors;
  };

  const passwordErrors = validatePassword(password);
  const passwordsMatch = password === confirmPassword || !confirmPassword;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation for registration
    if (!isLogin) {
      if (passwordErrors.length > 0) {
        setError('Password does not meet requirements');
        return;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setError('Please enter a valid email address');
        return;
      }
    }

    setLoading(true);

    try {
      if (isLogin) {
        // Login
        const data = await AuthService.login(username, password);
        AuthService.saveAuthData(data.access_token, username);
        setToken(data.access_token);
        if (setParentUsername) setParentUsername(username);
        setCurrentView('scanner');
      } else {
        // Register
        await AuthService.register(username, password, email || undefined);
        setSuccess('Registration successful! Please check your email to verify your account.');
        setIsLogin(true);
        setUsername('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto mt-10 p-8 glass rounded-2xl border border-neonBlue border-opacity-30 relative z-10 animate-fade-in">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-neonBlue/10 rounded-full mb-4">
          <Shield className="w-8 h-8 text-neonBlue" />
        </div>
        <h2 className="text-3xl font-bold font-mono text-neonBlue mb-2">
          {isLogin ? "Welcome Back" : "Create Account"}
        </h2>
        <p className="text-gray-400 text-sm">
          {isLogin 
            ? "Login to access your scan history and dashboard" 
            : "Join PhishGuard AI for advanced URL protection"}
        </p>
      </div>
      
      {/* Alerts */}
      {error && <Alert type="error" message={error} onClose={() => setError('')} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

      {/* Features List (Register only) */}
      {!isLogin && (
        <div className="mb-6 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
          <p className="text-xs font-bold text-gray-400 uppercase mb-3">Free Account Benefits:</p>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              Save unlimited scan history
            </li>
            <li className="flex items-center text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              Access detailed threat analytics
            </li>
            <li className="flex items-center text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              Track scanning patterns over time
            </li>
            <li className="flex items-center text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
              Export scan reports
            </li>
          </ul>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          icon={User}
          required
          disabled={loading}
        />
        
        {!isLogin && (
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email (optional but recommended)"
            icon={Mail}
            disabled={loading}
          />
        )}
        
        <div className="relative">
          <Input
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            icon={Lock}
            required
            disabled={loading}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>

        {/* Password Strength Indicator (Register only) */}
        {!isLogin && password && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Password Strength:</span>
              <span className={`font-bold ${passwordStrength.color}`}>{passwordStrength.level}</span>
            </div>
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${passwordStrength.bg}`}
                style={{ 
                  width: passwordStrength.level === 'Weak' ? '33%' : 
                         passwordStrength.level === 'Medium' ? '66%' : '100%' 
                }}
              ></div>
            </div>
            
            {/* Password Requirements */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              {[
                { label: '8+ characters', valid: password.length >= 8 },
                { label: 'Uppercase', valid: /[A-Z]/.test(password) },
                { label: 'Lowercase', valid: /[a-z]/.test(password) },
                { label: 'Number', valid: /[0-9]/.test(password) },
              ].map((req, idx) => (
                <div key={idx} className="flex items-center text-gray-400">
                  {req.valid ? (
                    <CheckCircle className="w-3 h-3 text-green-400 mr-1" />
                  ) : (
                    <XCircle className="w-3 h-3 text-red-400 mr-1" />
                  )}
                  <span className={req.valid ? 'text-green-400' : ''}>{req.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Confirm Password (Register only) */}
        {!isLogin && (
          <div>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm Password"
              icon={Lock}
              required
              disabled={loading}
            />
            {confirmPassword && !passwordsMatch && (
              <p className="text-red-400 text-xs mt-1 flex items-center">
                <XCircle className="w-3 h-3 mr-1" />
                Passwords do not match
              </p>
            )}
            {confirmPassword && passwordsMatch && (
              <p className="text-green-400 text-xs mt-1 flex items-center">
                <CheckCircle className="w-3 h-3 mr-1" />
                Passwords match
              </p>
            )}
          </div>
        )}

        <Button
          type="submit"
          variant="primary"
          loading={loading}
          className="w-full"
        >
          {isLogin ? (
            <><ArrowRight className="mr-2" /> Sign In</>
          ) : (
            <><UserPlus className="mr-2" /> Create Account</>
          )}
        </Button>
      </form>

      {/* Toggle Login/Register */}
      <div className="mt-6 pt-6 border-t border-gray-800 text-center">
        <p className="text-sm text-gray-400 mb-3">
          {isLogin ? "Don't have an account?" : "Already have an account?"}
        </p>
        <button 
          onClick={() => { 
            setIsLogin(!isLogin); 
            setError(''); 
            setSuccess('');
            setPassword('');
            setConfirmPassword('');
          }}
          className="text-neonBlue hover:text-white font-bold transition-colors"
          disabled={loading}
        >
          {isLogin ? "Sign up for free" : "Login instead"}
        </button>
      </div>

      {/* Security Notice */}
      <div className="mt-6 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
        <p className="text-xs text-blue-300 flex items-start">
          <Shield className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
          Your data is encrypted and securely stored. We never share your information.
        </p>
      </div>
    </div>
  );
}

export default Auth;
