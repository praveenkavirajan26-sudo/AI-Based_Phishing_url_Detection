// Utility Functions

import { RISK_LEVELS } from '../constants';

// Get risk level based on score
export function getRiskLevel(score) {
  if (score < RISK_LEVELS.SAFE.threshold) {
    return RISK_LEVELS.SAFE;
  } else if (score < RISK_LEVELS.SUSPICIOUS.threshold) {
    return RISK_LEVELS.SUSPICIOUS;
  } else {
    return RISK_LEVELS.DANGEROUS;
  }
}

// Format date string
export function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Truncate URL for display
export function truncateUrl(url, maxLength = 50) {
  if (url.length <= maxLength) return url;
  return url.substring(0, maxLength) + '...';
}

// Validate URL format
export function isValidUrl(string) {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}

// Get color class based on risk score
export function getRiskColorClass(score) {
  const level = getRiskLevel(score);
  return `text-${level.color}-500`;
}

// Get background color class based on risk score
export function getRiskBgClass(score) {
  const level = getRiskLevel(score);
  return `bg-${level.color}-500`;
}

// Calculate percentage width (capped at 100)
export function getPercentageWidth(value, max = 100) {
  return Math.min((value / max) * 100, 100);
}

// Debounce function
export function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Copy to clipboard
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
}

// Format number with commas
export function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Get feature display value
export function getFeatureDisplayValue(key, value) {
  // Binary features
  const binaryFeatures = [
    'has_https',
    'has_ip_address',
    'has_port',
    'tld_is_risky',
    'has_double_slash_redirect',
    'has_dns_record',
  ];

  if (binaryFeatures.includes(key)) {
    return value === 1 ? 'YES' : 'NO';
  }

  // Decimal features
  if (typeof value === 'number' && !Number.isInteger(value)) {
    return value.toFixed(3);
  }

  return value;
}

// Check if feature value is suspicious
export function isFeatureSuspicious(key, value) {
  const suspiciousConditions = {
    has_ip_address: (v) => v === 1,
    has_https: (v) => v === 0,
    tld_is_risky: (v) => v === 1,
    has_port: (v) => v === 1,
    has_double_slash_redirect: (v) => v === 1,
    num_suspicious_keywords: (v) => v > 0,
    num_at_symbols: (v) => v > 0,
    url_entropy: (v) => v > 4.5,
  };

  if (suspiciousConditions[key]) {
    return suspiciousConditions[key](value);
  }

  return false;
}
