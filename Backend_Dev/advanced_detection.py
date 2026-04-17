"""
advanced_detection.py - Rule-based detection for typosquatting and brand impersonation
This acts as a safety net before ML model prediction
"""
import re
from urllib.parse import urlparse


# Known brands that are commonly impersonated
KNOWN_BRANDS = [
    'google', 'facebook', 'amazon', 'paypal', 'microsoft', 'apple',
    'netflix', 'twitter', 'instagram', 'linkedin', 'github', 'youtube',
    'adobe', 'dropbox', 'spotify', 'whatsapp', 'telegram', 'discord',
    'steam', 'ebay', 'walmart', 'target', 'bestbuy', 'costco',
    'bankofamerica', 'chase', 'wellsfargo', 'citibank', 'capitalone',
    'visa', 'mastercard', 'americanexpress', 'discover',
    'office365', 'outlook', 'hotmail', 'gmail', 'yahoo',
    'icloud', 'onedrive', 'googledrive', 'dropbox'
]

# Common character substitutions used in typosquatting
CHAR_SUBSTITUTIONS = {
    '0': 'o',   # zero → o
    '1': 'l',   # one → l (lowercase L)
    '3': 'e',   # three → e
    '4': 'a',   # four → a
    '5': 's',   # five → s
    '7': 't',   # seven → t
    '@': 'a',   # at sign → a
    '!': 'i',   # exclamation → i
}

# Suspicious TLDs commonly used in phishing
SUSPICIOUS_TLDS = [
    '.xyz', '.top', '.club', '.tk', '.ml', '.ga', '.cf', '.gq',
    '.buzz', '.icu', '.site', '.online', '.store', '.tech', '.fun',
    '.space', '.website', '.link', '.click', '.help', '.info'
]


def extract_domain(url):
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Remove www. prefix
        domain = domain.replace('www.', '')
        # Remove port if present
        domain = domain.split(':')[0]
        return domain.lower()
    except:
        return url.lower()


def normalize_domain(domain):
    """Normalize domain by reversing common character substitutions."""
    normalized = domain
    for suspicious_char, real_char in CHAR_SUBSTITUTIONS.items():
        normalized = normalized.replace(suspicious_char, real_char)
    return normalized


def levenshtein_distance(s1, s2):
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def check_typosquatting(url):
    """
    Check if URL is typosquatting a known brand.
    
    Returns:
        dict: Detection result with score and details
    """
    domain = extract_domain(url)
    normalized = normalize_domain(domain)
    
    # Remove TLD for comparison
    domain_no_tld = domain.split('.')[0]
    normalized_no_tld = normalized.split('.')[0]
    
    suspicious_brands = []
    
    for brand in KNOWN_BRANDS:
        # Check exact match after normalization
        if normalized_no_tld == brand and domain_no_tld != brand:
            # Domain uses character substitution!
            suspicious_brands.append({
                'brand': brand,
                'type': 'character_substitution',
                'severity': 'HIGH',
                'details': f"Domain '{domain_no_tld}' uses character substitution to impersonate '{brand}'"
            })
        
        # Check Levenshtein distance (typosquatting)
        elif normalized_no_tld != brand:
            distance = levenshtein_distance(normalized_no_tld, brand)
            if distance <= 2 and distance > 0:
                # Very similar to known brand
                suspicious_brands.append({
                    'brand': brand,
                    'type': 'typosquatting',
                    'severity': 'HIGH' if distance == 1 else 'MEDIUM',
                    'details': f"Domain '{domain_no_tld}' is suspiciously similar to '{brand}' (distance: {distance})"
                })
    
    return {
        'detected': len(suspicious_brands) > 0,
        'risk_score': 95 if any(b['severity'] == 'HIGH' for b in suspicious_brands) else 70,
        'details': suspicious_brands,
        'count': len(suspicious_brands)
    }


def check_suspicious_patterns(url):
    """
    Check for other suspicious patterns in URL.
    
    Returns:
        dict: Detection result
    """
    indicators = []
    url_lower = url.lower()
    
    # Check for HTTP (not HTTPS) with sensitive keywords
    if url.startswith('http://'):
        sensitive_keywords = ['login', 'signin', 'account', 'verify', 'secure', 'update', 'confirm']
        if any(keyword in url_lower for keyword in sensitive_keywords):
            indicators.append({
                'type': 'insecure_connection',
                'severity': 'MEDIUM',
                'details': 'Using HTTP (not HTTPS) with sensitive keywords'
            })
    
    # Check for suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if url_lower.endswith(tld):
            indicators.append({
                'type': 'suspicious_tld',
                'severity': 'LOW',
                'details': f'Using suspicious TLD: {tld}'
            })
            break
    
    # Check for excessive subdomains
    domain = extract_domain(url)
    subdomains = domain.split('.')
    if len(subdomains) > 3:
        indicators.append({
            'type': 'excessive_subdomains',
            'severity': 'MEDIUM',
            'details': f'URL has {len(subdomains)-1} subdomains (potential phishing)'
        })
    
    # Check for IP address instead of domain
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    if re.search(ip_pattern, url):
        indicators.append({
            'type': 'ip_address',
            'severity': 'HIGH',
            'details': 'URL uses IP address instead of domain name'
        })
    
    # Check for URL shorteners (MEDIUM RISK - not all shorteners are phishing)
    shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'short.link']
    for shortener in shorteners:
        if shortener in url_lower:
            indicators.append({
                'type': 'url_shortener',
                'severity': 'MEDIUM',  # MEDIUM - shorteners alone aren't enough
                'details': f'Using URL shortener: {shortener} (hides real destination)'
            })
            break
    
    # Check for scam/phishing keywords (NEW!)
    scam_keywords = [
        'free', 'winner', 'congratulations', 'claim', 'prize', 'gift',
        'urgent', 'limited', 'act now', 'verify account', 'suspended',
        'update payment', 'confirm identity', 'unusual activity'
    ]
    
    scam_keyword_count = sum(1 for keyword in scam_keywords if keyword in url_lower)
    if scam_keyword_count >= 2:
        indicators.append({
            'type': 'scam_keywords',
            'severity': 'HIGH',
            'details': f'URL contains {scam_keyword_count} scam-related keywords: {", ".join([kw for kw in scam_keywords if kw in url_lower][:3])}'
        })
    elif scam_keyword_count == 1:
        indicators.append({
            'type': 'suspicious_keyword',
            'severity': 'MEDIUM',
            'details': f'URL contains suspicious keyword: {[kw for kw in scam_keywords if kw in url_lower][0]}'
        })
    
    # Check for brand names + scam keywords combination
    brands_in_url = [brand for brand in KNOWN_BRANDS if brand in url_lower]
    if brands_in_url and scam_keyword_count > 0:
        indicators.append({
            'type': 'brand_scam_combination',
            'severity': 'HIGH',
            'details': f'Brand impersonation detected: {", ".join(brands_in_url[:2])} + scam keywords'
        })
    
    return {
        'detected': len(indicators) > 0,
        'risk_score': min(100, sum({'HIGH': 40, 'MEDIUM': 20, 'LOW': 10}.get(i['severity'], 0) for i in indicators)),
        'details': indicators,
        'count': len(indicators)
    }


def advanced_url_analysis(url):
    """
    Comprehensive URL analysis combining all detection methods.
    
    Returns:
        dict: Complete analysis result
    """
    # Run all checks
    typosquatting = check_typosquatting(url)
    suspicious_patterns = check_suspicious_patterns(url)
    
    # Calculate combined risk score
    combined_score = max(
        typosquatting['risk_score'],
        suspicious_patterns['risk_score']
    )
    
    # Determine if should block - be conservative to avoid false positives
    # Only block if:
    # 1. Typosquatting detected (character substitution), OR
    # 2. Multiple HIGH severity indicators (2+), OR
    # 3. Very high risk score (90+) with at least 1 indicator
    should_block = (
        typosquatting['detected'] or  # Typosquatting is always bad
        (suspicious_patterns['count'] >= 2 and any(i['severity'] == 'HIGH' for i in suspicious_patterns['details'])) or
        (combined_score >= 90 and suspicious_patterns['count'] >= 1)
    )
    
    # Collect all findings
    all_findings = typosquatting['details'] + suspicious_patterns['details']
    
    return {
        'should_block': should_block,
        'risk_score': combined_score,
        'typosquatting': typosquatting,
        'suspicious_patterns': suspicious_patterns,
        'total_indicators': len(all_findings),
        'findings': all_findings,
        'recommendation': 'BLOCK' if should_block else 'ALLOW'
    }
