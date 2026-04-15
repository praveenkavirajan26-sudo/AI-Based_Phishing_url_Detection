"""
Build Real-World Phishing Dataset
Downloads phishing URLs from multiple sources and combines with legitimate URLs
"""
import pandas as pd
import requests
import time
from features import extract_features

def download_phishtank_data():
    """Download phishing URLs from PhishTank (requires app key)"""
    print("Downloading from PhishTank...")
    # PhishTank requires registration, so we'll use a public mirror
    try:
        url = "https://raw.githubusercontent.com/0xDanielLopez/TweetFeed/master/week.csv"
        df = pd.read_csv(url)
        # Extract URLs from the dataset
        phishing_urls = []
        for _, row in df.iterrows():
            if pd.notna(row.get('url')):
                phishing_urls.append(row['url'])
        print(f"✓ Downloaded {len(phishing_urls)} phishing URLs from TweetFeed")
        return phishing_urls[:5000]  # Limit to 5000
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return []

def download_urlhaus_data():
    """Download malicious URLs from URLHaus"""
    print("Downloading from URLHaus...")
    try:
        url = "https://urlhaus.abuse.ch/downloads/csv/"
        response = requests.get(url, timeout=30)
        lines = response.text.strip().split('\n')
        
        phishing_urls = []
        for line in lines[7:]:  # Skip header lines
            parts = line.split(',')
            if len(parts) >= 3 and 'phishing' in parts[2].lower():
                phishing_urls.append(parts[2].strip('"'))
        
        print(f"✓ Downloaded {len(phishing_urls)} phishing URLs from URLHaus")
        return phishing_urls[:5000]
    except Exception as e:
        print(f"✗ Error downloading URLHaus: {e}")
        return []

def get_legitimate_urls():
    """Generate legitimate URLs from known safe domains"""
    print("Generating legitimate URLs...")
    
    # Top 100 legitimate domains
    domains = [
        "google.com", "youtube.com", "facebook.com", "amazon.com", "wikipedia.org",
        "twitter.com", "instagram.com", "linkedin.com", "microsoft.com", "apple.com",
        "github.com", "stackoverflow.com", "reddit.com", "netflix.com", "spotify.com",
        "bbc.com", "cnn.com", "nytimes.com", "theguardian.com", "medium.com",
        "dropbox.com", "slack.com", "zoom.us", "shopify.com", "stripe.com",
        "yahoo.com", "mail.google.com", "drive.google.com", "docs.google.com",
        "maps.google.com", "play.google.com", "cloudflare.com", "wordpress.org",
        "github.io", "amazonaws.com", "azure.microsoft.com", "oracle.com",
        "ibm.com", "intel.com", "nvidia.com", "amd.com", "dell.com",
        "hp.com", "lenovo.com", "samsung.com", "sony.com", "lg.com",
        "adobe.com", "figma.com", "canva.com", "trello.com", "notion.so",
        "airbnb.com", "booking.com", "expedia.com", "tripadvisor.com", "yelp.com",
        "pinterest.com", "tumblr.com", "snapchat.com", "tiktok.com", "twitch.tv",
        "discord.com", "whatsapp.com", "telegram.org", "signal.org", "zoom.us",
        "salesforce.com", "hubspot.com", "mailchimp.com", "zendesk.com", "intercom.com",
        "paypal.com", "visa.com", "mastercard.com", "stripe.com", "square.com",
        "wellsfargo.com", "chase.com", "bankofamerica.com", "citibank.com", "capitalone.com",
        "edu.harvard.edu", "mit.edu", "stanford.edu", "berkeley.edu", "cmu.edu",
        "nih.gov", "cdc.gov", "nasa.gov", "noaa.gov", "usgs.gov",
        "whitehouse.gov", "state.gov", "treasury.gov", "defense.gov", "justice.gov"
    ]
    
    paths = [
        "/", "/about", "/contact", "/products", "/services",
        "/blog", "/news", "/faq", "/support", "/login",
        "/profile", "/settings", "/dashboard", "/search", "/help",
        "/docs", "/api", "/pricing", "/features", "/team",
        "/careers", "/privacy", "/terms", "/sitemap", "/feed"
    ]
    
    legitimate_urls = []
    for domain in domains:
        for path in paths[:20]:  # Use first 20 paths per domain
            scheme = "https"
            legitimate_urls.append(f"{scheme}://{domain}{path}")
    
    print(f"✓ Generated {len(legitimate_urls)} legitimate URLs")
    return legitimate_urls

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
            if (i + 1) % 500 == 0:
                print(f"  Processed {i + 1}/{len(phishing_urls)} phishing URLs")
        except Exception as e:
            continue
    
    # Process legitimate URLs
    print(f"Processing {len(legitimate_urls)} legitimate URLs...")
    for i, url in enumerate(legitimate_urls):
        try:
            feats = extract_features(url)
            feats["url"] = url
            feats["label"] = 0
            records.append(feats)
            if (i + 1) % 500 == 0:
                print(f"  Processed {i + 1}/{len(legitimate_urls)} legitimate URLs")
        except Exception as e:
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
    print("Building Real-World Phishing Dataset")
    print("=" * 60)
    
    # Download phishing URLs
    phishing_urls = []
    
    # Try URLHaus first
    urlhaus_urls = download_urlhaus_data()
    phishing_urls.extend(urlhaus_urls)
    
    # Try TweetFeed
    tweetfeed_urls = download_phishtank_data()
    phishing_urls.extend(tweetfeed_urls)
    
    # Remove duplicates
    phishing_urls = list(set(phishing_urls))
    print(f"\n✓ Total unique phishing URLs: {len(phishing_urls)}")
    
    # Get legitimate URLs
    legitimate_urls = get_legitimate_urls()
    
    # Balance dataset (use equal amounts)
    n_samples = min(len(phishing_urls), len(legitimate_urls), 5000)
    phishing_urls = phishing_urls[:n_samples]
    legitimate_urls = legitimate_urls[:n_samples]
    
    print(f"\nFinal dataset will have:")
    print(f"  Phishing URLs: {len(phishing_urls)}")
    print(f"  Legitimate URLs: {len(legitimate_urls)}")
    print(f"  Total: {len(phishing_urls) + len(legitimate_urls)}")
    
    # Extract features and save
    confirm = input("\nProceed with feature extraction? (y/n): ")
    if confirm.lower() == 'y':
        df = extract_and_save(phishing_urls, legitimate_urls)
        print("\n✓ Dataset creation complete!")
    else:
        print("Cancelled.")
