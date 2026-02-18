import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
import pickle
import os
import re

# Simple heuristic features + TF-IDF model for demo purposes
class PhishingDetector:
    def __init__(self):
        self.pipeline = None
        self.ensure_model()

    def ensure_model(self):
        # Check if we should retrain or load? For simplicity in this environment, 
        # let's just train a small model on init if not exists.
        # In a real production app, we would load existing weights.
        
        # Simulated dataset for demonstration
        data = {
            'url': [
                'google.com', 'facebook.com', 'youtube.com', 'amazon.com', 'wikipedia.org',
                'twitter.com', 'instagram.com', 'linkedin.com', 'reddit.com', 'netflix.com',
                'paypal-security-update.com', 'secure-login-bank.com', 'apple-id-verify.net',
                'g00gle.com', 'free-iphone-winner.com', 'account-update-required.xyz',
                'login.verify-account.com', 'track-package-delivery.info', 'irs-tax-refund.com',
                'microsoft-support-alert.tk'
            ],
            'label': [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 0 = Legitimate
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1   # 1 = Phishing
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Pipeline: Tokenize by chars/words -> Random Forest
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(tokenizer=self.tokenizer)),
            ('clf', RandomForestClassifier(n_estimators=100))
        ])
        
        self.pipeline.fit(df['url'], df['label'])
        
    def tokenizer(self, url):
        # Split by non-alphanumeric characters
        tokens = re.split(r'[/\-.]', url)
        return [t for t in tokens if t]

    def predict(self, url):
        # Basic heuristic checks first
        if not url:
            return {"status": "error", "message": "Empty URL"}
            
        prob = self.pipeline.predict_proba([url])[0][1] # Probability of being phishing (class 1)
        prediction = self.pipeline.predict([url])[0]
        
        risk_score = round(prob * 100, 2)
        
        result = {
            "url": url,
            "is_phishing": bool(prediction),
            "risk_score": risk_score,
            "verdict": "Likely Phishing" if prediction else "Safe",
            "details": self.explain(url, risk_score)
        }
        return result

    def explain(self, url, score):
        reasons = []
        if len(url) > 50:
            reasons.append("Long URL length detected.")
        if "-" in url:
            reasons.append("Hypens detected in domain.")
        if "@" in url:
            reasons.append("Symbol '@' detected (often used for credential theft).")
        if score > 80:
             reasons.append("High similarity to known phishing patterns.")
        elif score > 50:
             reasons.append("Suspicious patterns detected.")
        else:
            reasons.append("Safe domain structure.")
            
        return reasons

detector = PhishingDetector()
