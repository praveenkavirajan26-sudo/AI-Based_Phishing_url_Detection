"""
Enhanced Dataset Builder - Prevents Overfitting
Creates diverse, realistic dataset with proper complexity
"""
import pandas as pd
import random
import string
from features import extract_features

random.seed(42)

def generate_diverse_legitimate_urls(count=5000):
    """Generate diverse legitimate URLs with variations"""
    print(f"Generating {count} diverse legitimate URLs...")
    
    # More domains with variety
    base_domains = [
        "google", "youtube", "facebook", "amazon", "wikipedia",
        "twitter", "instagram", "linkedin", "microsoft", "apple",
        "github", "stackoverflow", "reddit", "netflix", "spotify",
        "bbc", "cnn", "nytimes", "theguardian", "medium",
        "dropbox", "slack", "zoom", "shopify", "stripe",
        "yahoo", "adobe", "salesforce", "oracle", "ibm",
        "dell", "hp", "lenovo", "samsung", "sony",
        "paypal", "visa", "mastercard", "wellsfargo", "chase"
    ]
    
    tlds = [".com", ".org", ".net", ".edu", ".gov", ".io", ".co.uk", ".co", ".info", ".biz"]
    
    subdomains = ["www", "m", "api", "app", "blog", "docs", "mail", "cdn", "static", ""]
    
    paths = [
        "/", "/about", "/contact", "/products", "/services",
        "/blog/post-123", "/news/article-456", "/faq", "/support/ticket-789",
        "/login", "/profile/user123", "/settings/account", "/dashboard",
        "/search?q=python+programming", "/api/v1/users", "/docs/guide",
        "/pricing/plan", "/features/overview", "/team/members",
        "/careers/job-123", "/privacy-policy", "/terms-of-service",
        "/sitemap.xml", "/feed/rss", "/images/logo.png",
        "/css/style.css", "/js/app.js", "/assets/fonts/arial.woff2"
    ]
    
    params = [
        "",
        "?utm_source=google&utm_medium=search",
        "?ref=homepage&lang=en",
        "?page=1&limit=20&sort=name",
        "?id=12345&token=abc123xyz",
        "?category=tech&subcategory=ai",
        "?q=search+query+terms&filter=recent"
    ]
    
    urls = []
    while len(urls) < count:
        domain = random.choice(base_domains)
        # Add random suffix to create variety
        if random.random() > 0.7:
            domain += str(random.randint(1, 999))
        
        tld = random.choice(tlds)
        subdomain = random.choice(subdomains)
        path = random.choice(paths)
        param = random.choice(params)
        scheme = "https" if random.random() > 0.05 else "http"
        
        url = f"{scheme}://{subdomain}.{domain}{tld}{path}{param}"
        urls.append(url)
    
    print(f"✓ Generated {len(urls)} legitimate URLs")
    return urls

def generate_realistic_phishing_urls(count=5000):
    """Generate realistic phishing URLs with diverse tactics"""
    print(f"Generating {count} realistic phishing URLs...")
    
    targeted_brands = [
        "paypal", "amazon", "apple", "microsoft", "netflix",
        "facebook", "instagram", "twitter", "linkedin", "google",
        "chase", "wellsfargo", "bankofamerica", "citibank", "capitalone",
        "ebay", "shopify", "stripe", "square", "paypal",
        "dropbox", "adobe", "office365", "icloud", "yahoo"
    ]
    
    phishing_tactics = [
        # Tactic 1: Brand impersonation with suspicious TLD
        lambda: f"http://{random.choice(targeted_brands)}-secure.{random.choice(['.xyz', '.tk', '.ml', '.top', '.online'])}/login/verify",
        
        # Tactic 2: Subdomain spoofing
        lambda: f"http://{random.choice(targeted_brands)}.{random.choice(['verify', 'secure', 'login', 'account', 'update'])}.{random.choice(['.com', '.net', '.org'])}/signin",
        
        # Tactic 3: IP-based URLs
        lambda: f"http://{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}/{random.choice(targeted_brands)}/login",
        
        # Tactic 4: URL with suspicious parameters
        lambda: f"http://www.{random.choice(targeted_brands)}-verify.com/account/update?user=victim&token={random_string(16)}&redirect=http://evil.com",
        
        # Tactic 5: Homograph attacks (lookalike characters)
        lambda: f"http://www.{random.choice(targeted_breds)}-sеcurе.com/login",  # Uses Cyrillic е
        
        # Tactic 6: Long obfuscated URLs
        lambda: f"http://{random_string(20)}.{random.choice(['.xyz', '.tk'])}/{'/'.join([random_string(8) for _ in range(5)])}?{'&'.join([f'{random_string(5)}={random_string(10)}' for _ in range(5)])}",
        
        # Tactic 7: Double slash redirect
        lambda: f"http://{random.choice(targeted_brands)}.com//{random.choice(['login', 'verify', 'account'])}//{random.choice(['secure', 'update'])}?next=http://malicious.com",
        
        # Tactic 8: Port number abuse
        lambda: f"http://{random.choice(targeted_brands)}.com:{random.choice(['8080', '8443', '3000', '5000', '9090'])}/admin/login",
        
        # Tactic 9: Encoded characters
        lambda: f"http://{random.choice(targeted_brands)}-verify.com/login%2Fsecure%3Fuser%3D{random_string(10)}",
        
        # Tactic 10: Mixed case and special chars
        lambda: f"http://{random.choice(targeted_brands).upper()}-{random_string(5).lower()}.xyz/LoGiN/SeCuRe"
    ]
    
    urls = []
    while len(urls) < count:
        try:
            tactic = random.choice(phishing_tactics)
            url = tactic()
            urls.append(url)
        except:
            continue
    
    print(f"✓ Generated {len(urls)} phishing URLs")
    return urls

def random_string(length=10):
    """Generate random alphanumeric string"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def extract_and_save(phishing_urls, legitimate_urls, output_path="dataset.csv"):
    """Extract features and save dataset"""
    print("\nExtracting features...")
    
    records = []
    
    # Process phishing URLs
    print(f"Processing {len(phishing_urls)} phishing URLs...")
    for i, url in enumerate(phishing_urls):
        try:
            feats = extract_features(url)
            feats["url"] = url
            feats["label"] = 1
            records.append(feats)
            if (i + 1) % 1000 == 0:
                print(f"  Processed {i + 1}/{len(phishing_urls)} phishing URLs")
        except:
            continue
    
    # Process legitimate URLs
    print(f"Processing {len(legitimate_urls)} legitimate URLs...")
    for i, url in enumerate(legitimate_urls):
        try:
            feats = extract_features(url)
            feats["url"] = url
            feats["label"] = 0
            records.append(feats)
            if (i + 1) % 1000 == 0:
                print(f"  Processed {i + 1}/{len(legitimate_urls)} legitimate URLs")
        except:
            continue
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Dataset saved to {output_path}")
    print(f"  Total rows: {len(df)}")
    print(f"  Phishing: {df['label'].sum()}")
    print(f"  Legitimate: {(df['label'] == 0).sum()}")
    
    return df

if __name__ == "__main__":
    print("=" * 60)
    print("Building Enhanced Phishing Dataset (Prevents Overfitting)")
    print("=" * 60)
    
    # Generate balanced dataset
    n_samples = 5000
    
    phishing_urls = generate_realistic_phishing_urls(n_samples)
    legitimate_urls = generate_diverse_legitimate_urls(n_samples)
    
    print(f"\nFinal dataset:")
    print(f"  Phishing URLs: {len(phishing_urls)}")
    print(f"  Legitimate URLs: {len(legitimate_urls)}")
    print(f"  Total: {len(phishing_urls) + len(legitimate_urls)}")
    
    confirm = input("\nProceed with feature extraction? (y/n): ")
    if confirm.lower() == 'y':
        df = extract_and_save(phishing_urls, legitimate_urls)
        print("\n✓ Enhanced dataset creation complete!")
        print("\nNext steps:")
        print("1. Run: .\\venv\\Scripts\\python.exe train.py")
        print("2. Restart backend server")
        print("3. Test with real URLs")
    else:
        print("Cancelled.")
