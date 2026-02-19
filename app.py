from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import os
import re
from utils import extract_features
# Attempt to import pyzbar, handle potential import error gracefully
try:
    from pyzbar.pyzbar import decode
    PYZBAR_Available = True
except ImportError:
    PYZBAR_Available = False
    print("Warning: pyzbar not installed. QR code scanning might be limited.")

# Attempt to import cv2 as fallback
try:
    import cv2
    CV2_Available = True
except ImportError:
    CV2_Available = False
    print("Warning: opencv-python-headless not installed. QR code fallback disabled.")

from PIL import Image
import io

app = Flask(__name__)

# Load model
MODEL_PATH = 'models/phishing_model.pkl'
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
    else:
        print(f"Model file not found at {MODEL_PATH}. Prediction service unavailable.")

load_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    if not model:
        # Try loading again just in case
        load_model()
        if not model:
            return jsonify({'error': 'Model not loaded. Please train the model first.'}), 503
    
    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400
    
    url = data['url']
    
    # whitelist check
    whitelist = [
        'wa.me', 'www.wa.me', 'whatsapp.com', 'www.whatsapp.com', 
        'web.whatsapp.com', 'instagram.com', 'www.instagram.com', 
        'facebook.com', 'www.facebook.com', 'linkedin.com', 'www.linkedin.com',
        'twitter.com', 'www.twitter.com', 't.me', 'telegram.org',
        'google.com', 'www.google.com', 'youtube.com', 'www.youtube.com'
    ]
    
    domain = None
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
    except:
        pass
        
    if domain and any(safe_domain in domain for safe_domain in whitelist):
         return jsonify({
            'result': "Legitimate",
            'confidence': "100.0% (Whitelisted)",
            'url': url
        })

    try:
        features = np.array([extract_features(url)])
        prediction = model.predict(features)[0]
        # prediction 0 = Legitimate, 1 = Phishing
        result = "Phishing" if prediction == 1 else "Legitimate"
        
        # Get probability (confidence)
        proba = model.predict_proba(features)[0]
        confidence = proba[prediction] * 100
        
        return jsonify({
            'result': result,
            'confidence': f"{confidence:.1f}%",
            'url': url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan_qr', methods=['POST'])
def scan_qr():
    if not PYZBAR_Available and not CV2_Available:
        return jsonify({'error': 'QR Code scanning libraries (pyzbar/opencv) not available on server.'}), 501
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        # Read image
        img = Image.open(file.stream)
        url = None
        
        # Try pyzbar first
        if PYZBAR_Available:
            decoded_objects = decode(img)
            if decoded_objects:
                url = decoded_objects[0].data.decode('utf-8')
        
        # Try cv2 if pyzbar failed or not available
        if not url and CV2_Available:
            try:
                # Convert PIL image to cv2 format (numpy array)
                img_np = np.array(img.convert('RGB'))
                open_cv_image = img_np[:, :, ::-1].copy() # Convert RGB to BGR
                detector = cv2.QRCodeDetector()
                data, bbox, _ = detector.detectAndDecode(open_cv_image)
                if data:
                    url = data
            except Exception as cv_e:
                print(f"OpenCV decoding error: {cv_e}")

        if not url:
            return jsonify({'error': 'No QR code found in image'}), 400
            
        # Check if the content is actually a URL
        is_url_pattern = re.match(r'^(http|https|ftp)://', url, re.IGNORECASE) or \
                         re.match(r'^(www\.)', url, re.IGNORECASE)
        
        result = "Legitimate" # Default to Legitimate for non-URLs like WiFi/Contact cards
        confidence = "Safe (Non-URL)"
        
        if is_url_pattern:
             # whitelist check
            whitelist = [
                'wa.me', 'www.wa.me', 'whatsapp.com', 'www.whatsapp.com', 
                'web.whatsapp.com', 'instagram.com', 'www.instagram.com', 
                'facebook.com', 'www.facebook.com', 'linkedin.com', 'www.linkedin.com',
                'twitter.com', 'www.twitter.com', 't.me', 'telegram.org',
                'google.com', 'www.google.com', 'youtube.com', 'www.youtube.com'
            ]
            
            domain = None
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
            except:
                pass
                
            if domain and any(safe_domain in domain for safe_domain in whitelist):
                result = "Legitimate"
                confidence = "100.0% (Whitelisted)"
            elif model:
                features = np.array([extract_features(url)])
                prediction = model.predict(features)[0]
                result = "Phishing" if prediction == 1 else "Legitimate"
                proba = model.predict_proba(features)[0]
                confidence = f"{proba[prediction] * 100:.1f}%"
        else:
             # It's raw text, WiFi config, or app data (like WhatsApp Web)
             result = "Legitimate"
             confidence = "100% (Not a URL)"

        return jsonify({
            'url': url,
            'result': result,
            'confidence': confidence
        })
        
    except Exception as e:
        return jsonify({'error': f"Error processing QR code: {str(e)}"}), 500

if __name__ == '__main__':
    import socket
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"\n * Running on http://{local_ip}:3000 (Press CTRL+C to quit)\n")
    except Exception:
        print("\n * Could not determine local IP. Running on http://127.0.0.1:3000\n")

    app.run(host='0.0.0.0', debug=True, port=3000)
