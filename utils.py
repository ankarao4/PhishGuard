import re
from urllib.parse import urlparse

def extract_features(url):
    """
    Extracts features from a URL for phishing detection.
    Returns a list of numerical features.
    """
    features = []
    
    # Feature 1: URL Length
    features.append(len(url))
    
    # Feature 2: Number of dots
    features.append(url.count('.'))
    
    # Feature 3: Has IP address (simple regex check)
    ip_pattern = re.search(r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\/)|'  # IPv4
                            r'((0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\/)' # Hexadecimal
                            r'(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url) # IPv6
    features.append(1 if ip_pattern else 0)
    
    # Feature 4: Presence of @ symbol
    features.append(1 if '@' in url else 0)
    
    # Feature 5: Path Length
    parsed_url = urlparse(url)
    features.append(len(parsed_url.path))
    
    # Feature 6: Is HTTPS
    features.append(1 if parsed_url.scheme == 'https' else 0)
    
    # Feature 7: Presence of suspicious keywords
    suspicious_keywords = ['login', 'secure', 'account', 'update', 'banking', 'verify']
    features.append(sum(1 for keyword in suspicious_keywords if keyword in url.lower()))

    # Feature 8: Number of special characters in path
    features.append(len(re.findall(r'[!@#$%^&*(),?":{}|<>]', parsed_url.path)))
    
    return features
