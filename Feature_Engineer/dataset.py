# pyre-ignore-all-errors
"""
Dataset Generator for Phishing URL Detection.
Generates a realistic synthetic dataset of 12,000 URLs
(6,000 legitimate + 6,000 phishing) with full feature extraction.
"""

import random
import string
import pandas as pd
from features import extract_features, FEATURE_NAMES

random.seed(42)

# ── URL Component Pools ───────────────────────────────────────────────────────

LEGIT_DOMAINS = [
    "google", "youtube", "facebook", "amazon", "wikipedia",
    "twitter", "instagram", "linkedin", "microsoft", "apple",
    "github", "stackoverflow", "reddit", "netflix", "spotify",
    "bbc", "cnn", "nytimes", "theguardian", "medium",
    "dropbox", "slack", "zoom", "shopify", "stripe",
]
LEGIT_TLDS = [".com", ".org", ".net", ".edu", ".gov", ".io", ".co.uk"]
LEGIT_PATHS = [
    "/", "/about", "/contact", "/products", "/services",
    "/blog", "/news", "/faq", "/support", "/login",
    "/profile", "/settings", "/dashboard", "/search",
]

PHISHING_WORDS = [
    "secure", "login", "verify", "update", "account", "bank",
    "paypal", "ebay", "amazon", "apple", "microsoft", "netflix",
    "confirm", "alert", "unlock", "suspended", "validate",
]
PHISHING_FAKE_TLDS = [".xyz", ".tk", ".ml", ".top", ".online", ".site", ".icu"]
PHISHING_TACTICS = [
    lambda d, t: f"http://{d}-secure{t}/login/verify",
    lambda d, t: f"http://secure-{d}{t}/account/update",
    lambda d, t: f"http://192.168.{random.randint(1,255)}.{random.randint(1,255)}/{d}/login",
    lambda d, t: f"http://{d}.verify-account{t}/signin",
    lambda d, t: f"http://{random.choice(PHISHING_WORDS)}-{d}{t}/confirm?user=victim&token=abc123",
    lambda d, t: f"http://{d}{random.randint(100,9999)}{t}/update-info",
    lambda d, t: f"http://free-{d}-login{t}/auth/password",
    lambda d, t: f"http://{d}.{random.choice(PHISHING_WORDS)}{t}/verify-now?redirect=https://real.com",
]


def _rand_str(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def _generate_legit_url() -> str:
    domain = random.choice(LEGIT_DOMAINS)
    tld    = random.choice(LEGIT_TLDS)
    path   = random.choice(LEGIT_PATHS)
    subdomain = random.choice(["www.", "m.", "api.", ""])
    scheme = "https" if random.random() > 0.1 else "http"
    return f"{scheme}://{subdomain}{domain}{tld}{path}"


def _generate_phishing_url() -> str:
    domain = random.choice(PHISHING_WORDS + LEGIT_DOMAINS)
    tld    = random.choice(PHISHING_FAKE_TLDS + [".com", ".net"])
    tactic = random.choice(PHISHING_TACTICS)
    return tactic(domain, tld)


def generate_dataset(n_legit: int = 2000, n_phishing: int = 2000,
                     output_path: str = "dataset.csv") -> pd.DataFrame:
    print(f"Generating {n_legit} legitimate + {n_phishing} phishing URLs...")

    records = []

    for _ in range(n_legit):
        url = _generate_legit_url()
        feats = extract_features(url)
        feats["url"] = url
        feats["label"] = 0
        records.append(feats)

    for _ in range(n_phishing):
        url = _generate_phishing_url()
        feats = extract_features(url)
        feats["url"] = url
        feats["label"] = 1
        records.append(feats)

    df = pd.DataFrame(records)
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    df.to_csv(output_path, index=False)
    print(f"Dataset saved -> {output_path}  ({len(df)} rows, {df['label'].sum()} phishing)")
    return df


if __name__ == "__main__":
    generate_dataset()
