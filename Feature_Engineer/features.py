# pyre-ignore-all-errors
"""
Feature Engineering Module for Phishing URL Detection
Extracts 20+ features from raw URLs.
"""

import re
import math
import socket
import urllib.parse
from collections import Counter

# ── Optional imports (graceful fallback) ─────────────────────────────────────
try:
    import tldextract
    HAS_TLDEXTRACT = True
except ImportError:
    HAS_TLDEXTRACT = False

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

# ── Constants ─────────────────────────────────────────────────────────────────
SUSPICIOUS_KEYWORDS = ["login", "secure", "verify", "update", "bank",
                       "account", "signin", "auth", "confirm", "password",
                       "ebay", "paypal", "free", "lucky", "service", "bonus"]

RISKY_TLDS = {'.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.club',
              '.online', '.site', '.icu', '.pw', '.cc', '.su'}

FEATURE_NAMES = [
    "url_length",
    "num_dots",
    "num_hyphens",
    "num_at_symbols",
    "num_slashes",
    "num_question_marks",
    "num_equal_signs",
    "num_underscores",
    "has_ip_address",
    "has_https",
    "domain_length",
    "num_subdomains",
    "path_length",
    "query_length",
    "has_port",
    "digit_to_letter_ratio",
    "num_special_chars",
    "url_entropy",
    "num_suspicious_keywords",
    "has_double_slash_redirect",
    "tld_is_risky",
    "num_digits",
    "num_letters",
    "url_depth",
    "has_dns_record",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _has_ip_address(url: str) -> int:
    """Check if URL contains an IP address instead of a domain."""
    ip_pattern = re.compile(
        r'((\d{1,3}\.){3}\d{1,3})'
    )
    return int(bool(ip_pattern.search(url)))


def _url_entropy(url: str) -> float:
    """Calculate Shannon entropy of URL string."""
    if not url:
        return 0.0
    freq = Counter(url)
    length = len(url)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def _has_dns_record(domain: str) -> int:
    """Return 1 if DNS A-record exists, 0 otherwise. Disabled for fast training."""
    return 0


def _extract_domain_info(url: str):
    """Return (domain, suffix, subdomain) via tldextract or basic parse."""
    if HAS_TLDEXTRACT:
        ext = tldextract.extract(url)
        return ext.domain, ext.suffix, ext.subdomain
    else:
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc.split(':')[0]   # strip port
            parts = netloc.split('.')
            if len(parts) >= 2:
                domain = parts[-2]
                suffix = '.' + parts[-1]
                subdomain = '.'.join(parts[:-2])
            else:
                domain = netloc
                suffix = ''
                subdomain = ''
            return domain, suffix, subdomain
        except Exception:
            return '', '', ''


# ── Main Feature Extractor ────────────────────────────────────────────────────

def extract_features(url: str) -> dict:
    """
    Extract 25 features from a URL string.
    Returns an ordered dict matching FEATURE_NAMES.
    """
    url = url.strip()

    # ── Parse URL ────────────────────────────────────────────────────────────
    try:
        parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
    except Exception:
        parsed = urllib.parse.urlparse('http://unknown.com')

    netloc   = parsed.netloc or ''
    path     = parsed.path    or ''
    query    = parsed.query   or ''
    scheme   = parsed.scheme  or ''

    domain, suffix, subdomain = _extract_domain_info(url)

    # ── Feature 1-8: Character-level URL stats ────────────────────────────────
    url_length        = len(url)
    num_dots          = url.count('.')
    num_hyphens       = url.count('-')
    num_at            = url.count('@')
    num_slashes       = url.count('/')
    num_question      = url.count('?')
    num_equal         = url.count('=')
    num_underscores   = url.count('_')

    # ── Feature 9-10: Binary flags ────────────────────────────────────────────
    has_ip            = _has_ip_address(url)
    has_https         = int(scheme.lower() == 'https')

    # ── Feature 11-14: Domain / path stats ───────────────────────────────────
    # Strip port from netloc for domain length
    clean_netloc      = netloc.split(':')[0]
    domain_length     = len(clean_netloc)
    num_subdomains    = len(subdomain.split('.')) if subdomain else 0
    path_length       = len(path)
    query_length      = len(query)

    # ── Feature 15: Port presence ─────────────────────────────────────────────
    has_port          = int(':' in netloc and netloc.split(':')[-1].isdigit())

    # ── Feature 16-17: Digit/letter ratios and special chars ─────────────────
    digits            = sum(c.isdigit() for c in url)
    letters           = sum(c.isalpha() for c in url)
    digit_letter_ratio = digits / (letters + 1)          # +1 to avoid div/0
    special_chars     = len(re.findall(r'[^a-zA-Z0-9\-_./:]', url))

    # ── Feature 18: Entropy ────────────────────────────────────────────────────
    entropy           = _url_entropy(url)

    # ── Feature 19: Suspicious keywords ───────────────────────────────────────
    url_lower         = url.lower()
    num_suspicious    = sum(kw in url_lower for kw in SUSPICIOUS_KEYWORDS)

    # ── Feature 20: Double-slash redirect ─────────────────────────────────────
    has_double_slash  = int('//' in url[8:])   # ignore scheme's //

    # ── Feature 21: Risky TLD ─────────────────────────────────────────────────
    tld_risky         = int(('.' + suffix) in RISKY_TLDS or suffix in RISKY_TLDS)

    # ── Feature 22-23: Raw digit/letter counts ────────────────────────────────
    num_digits        = digits
    num_letters       = letters

    # ── Feature 24: URL depth (number of path segments) ──────────────────────
    url_depth         = len([p for p in path.split('/') if p])

    # ── Feature 25: DNS record existence ──────────────────────────────────────
    has_dns           = _has_dns_record(clean_netloc)

    features = {
        "url_length":               url_length,
        "num_dots":                 num_dots,
        "num_hyphens":              num_hyphens,
        "num_at_symbols":           num_at,
        "num_slashes":              num_slashes,
        "num_question_marks":       num_question,
        "num_equal_signs":          num_equal,
        "num_underscores":          num_underscores,
        "has_ip_address":           has_ip,
        "has_https":                has_https,
        "domain_length":            domain_length,
        "num_subdomains":           num_subdomains,
        "path_length":              path_length,
        "query_length":             query_length,
        "has_port":                 has_port,
        "digit_to_letter_ratio":    round(digit_letter_ratio, 4),
        "num_special_chars":        special_chars,
        "url_entropy":              round(entropy, 4),
        "num_suspicious_keywords":  num_suspicious,
        "has_double_slash_redirect": has_double_slash,
        "tld_is_risky":             tld_risky,
        "num_digits":               num_digits,
        "num_letters":              num_letters,
        "url_depth":                url_depth,
        "has_dns_record":           has_dns,
    }
    return features


def features_to_list(url: str) -> list:
    """Return feature values as a plain list (matches FEATURE_NAMES order)."""
    d = extract_features(url)
    return [d[k] for k in FEATURE_NAMES]
