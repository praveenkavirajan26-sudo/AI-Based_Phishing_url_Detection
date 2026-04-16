import React from 'react';

// Alert component for showing messages
export function Alert({ type = 'error', message, onClose }) {
  const styles = {
    error: 'bg-red-900/30 text-red-400 border-red-500',
    success: 'bg-green-900/30 text-green-400 border-green-500',
    warning: 'bg-yellow-900/30 text-yellow-400 border-yellow-500',
    info: 'bg-blue-900/30 text-blue-400 border-blue-500',
  };

  return (
    <div className={`p-3 mb-4 rounded text-sm border ${styles[type]} relative`}>
      {onClose && (
        <button
          onClick={onClose}
          className="absolute right-2 top-2 text-lg leading-none opacity-50 hover:opacity-100"
        >
          ×
        </button>
      )}
      {message}
    </div>
  );
}

// Loading spinner component
export function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`${sizes[size]} border-4 border-neonBlue border-t-transparent rounded-full animate-spin`}></div>
      {text && <p className="mt-4 text-neonBlue font-mono text-sm">{text}</p>}
    </div>
  );
}

// Button component
export function Button({ 
  children, 
  onClick, 
  type = 'button',
  variant = 'primary',
  disabled = false,
  loading = false,
  className = '',
}) {
  const variants = {
    primary: 'bg-neonBlue text-black hover:bg-white',
    secondary: 'bg-gray-800 text-white hover:bg-gray-700',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    ghost: 'bg-transparent text-neonBlue hover:bg-gray-800',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        px-6 py-3 rounded-xl font-bold transition-all
        ${variants[variant]}
        ${(disabled || loading) ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      {loading ? (
        <span className="flex items-center justify-center">
          <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Processing...
        </span>
      ) : (
        children
      )}
    </button>
  );
}

// Input component
export function Input({
  type = 'text',
  value,
  onChange,
  placeholder,
  icon: Icon,
  required = false,
  disabled = false,
  className = '',
}) {
  return (
    <div className="relative">
      {Icon && (
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        className={`
          w-full bg-gray-900 border border-gray-700 rounded-xl
          py-3 ${Icon ? 'px-10' : 'px-4'}
          text-white placeholder-gray-500
          focus:outline-none focus:border-neonBlue focus:ring-1 focus:ring-neonBlue
          transition-colors disabled:opacity-50
          ${className}
        `}
      />
    </div>
  );
}

// Card component
export function Card({ children, className = '', bordered = true }) {
  return (
    <div
      className={`
        glass rounded-2xl p-6
        ${bordered ? 'border border-gray-800' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

// Badge component
export function Badge({ children, variant = 'default' }) {
  const variants = {
    default: 'bg-gray-800 text-gray-300',
    success: 'bg-green-900/30 text-green-400 border border-green-500',
    danger: 'bg-red-900/30 text-red-400 border border-red-500',
    warning: 'bg-yellow-900/30 text-yellow-400 border border-yellow-500',
    info: 'bg-blue-900/30 text-blue-400 border border-blue-500',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold ${variants[variant]}`}>
      {children}
    </span>
  );
}
