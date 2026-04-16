// Application Constants

export const RISK_LEVELS = {
  SAFE: { label: 'SAFE', threshold: 30, color: 'green' },
  SUSPICIOUS: { label: 'SUSPICIOUS', threshold: 70, color: 'yellow' },
  DANGEROUS: { label: 'DANGEROUS', threshold: 100, color: 'red' },
};

export const PREDICTIONS = {
  PHISHING: 'Phishing',
  LEGITIMATE: 'Legitimate',
};

export const STORAGE_KEYS = {
  TOKEN: 'token',
  USERNAME: 'username',
};

export const ROUTES = {
  SCANNER: 'scanner',
  OUTPUT: 'output',
  DASHBOARD: 'dashboard',
  AUTH: 'auth',
};

export const FEATURE_DESCRIPTIONS = {
  url_length: 'Total character count of the URL',
  num_dots: 'Number of dots in URL',
  num_hyphens: 'Number of hyphens in URL',
  num_at_symbols: 'Number of @ symbols (suspicious)',
  num_slashes: 'Number of forward slashes',
  num_question_marks: 'Number of query parameters',
  num_equal_signs: 'Number of key-value pairs',
  num_underscores: 'Number of underscores',
  has_ip_address: 'Uses IP address instead of domain',
  has_https: 'Uses HTTPS protocol',
  domain_length: 'Length of domain name',
  num_subdomains: 'Number of subdomains',
  path_length: 'Length of URL path',
  query_length: 'Length of query string',
  has_port: 'Has non-standard port number',
  digit_to_letter_ratio: 'Ratio of digits to letters',
  num_special_chars: 'Number of special characters',
  url_entropy: 'Shannon entropy (randomness)',
  num_suspicious_keywords: 'Count of suspicious words',
  has_double_slash_redirect: 'Has double slash redirect',
  tld_is_risky: 'Uses risky TLD (.xyz, .tk, etc)',
  num_digits: 'Total digit count',
  num_letters: 'Total letter count',
  url_depth: 'Number of path segments',
  has_dns_record: 'DNS record exists',
};
