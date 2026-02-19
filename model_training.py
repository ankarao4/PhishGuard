import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
from utils import extract_features

# Generate synthetic dataset
def generate_synthetic_data(num_samples=2000):
    urls = []
    labels = []
    
    # Legitimate URLs
    legitimate_domains = [
        'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'wikipedia.org', 
        'yahoo.com', 'reddit.com', 'netflix.com', 'stackoverflow.com', 'github.com',
        'whatsapp.com', 'web.whatsapp.com', 'wa.me', 'instagram.com', 'linkedin.com', 
        'twitter.com', 'x.com', 't.me', 'telegram.org', 'microsoft.com', 'apple.com'
    ]
    paths = ['', '/login', '/home', '/dashboard', '/user/profile', '/search', '/articles/2023', '/products/item123']
    
    for _ in range(num_samples // 2):
        domain = np.random.choice(legitimate_domains)
        path = np.random.choice(paths)
        url = f"https://www.{domain}{path}"
        urls.append(url)
        labels.append(0) # 0 for Legitimate

    # Phishing URLs
    phishing_domains = ['secure-login-update.com', 'account-verification-required.net', 'paypal-secure-login.com', 'apple-support-center.org', 'bank-of-america-verify.com', 'microsoft-security-alert.net']
    phishing_paths = ['/login.php?user=admin', '/verify-account', '/update-payment-info', '/secure/banking', '/confirm-identity', '/reset-password']
    
    for _ in range(num_samples // 2):
        domain = np.random.choice(phishing_domains)
        path = np.random.choice(phishing_paths)
        # Add some variation
        if np.random.random() > 0.5:
            url = f"http://{domain}{path}" # Often http
        else:
            url = f"https://{domain}{path}" # Phishing sites use https too
            
        # Add IP address URLs occasionally
        if np.random.random() > 0.8:
            ip = ".".join(map(str, (np.random.randint(0, 256) for _ in range(4))))
            url = f"http://{ip}{path}"
            
        urls.append(url)
        labels.append(1) # 1 for Phishing
        
    return pd.DataFrame({'url': urls, 'label': labels})

def train_model():
    print("Generating synthetic dataset...")
    df = generate_synthetic_data()
    
    print("Extracting features...")
    X = [extract_features(url) for url in df['url']]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # Save the model
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/phishing_model.pkl')
    print("Model saved to models/phishing_model.pkl")

if __name__ == "__main__":
    train_model()
