from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from model import detector
import ctypes
import os

# MacOS specific fix for pyzbar not finding libzbar
try:
    libzbar_path = '/opt/homebrew/opt/zbar/lib/libzbar.dylib'
    if os.path.exists(libzbar_path):
        ctypes.CDLL(libzbar_path)
except Exception as e:
    print(f"Warning: Could not manually load libzbar: {e}")

try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("Warning: pyzbar not available, falling back to OpenCV")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict-url', methods=['POST'])
def predict_url():
    data = request.json
    url = data.get('url', '')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    result = detector.predict(url)
    return jsonify(result)

@app.route('/analyze-qr', methods=['POST'])
def analyze_qr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Process image
    try:
        # Read file into numpy array
        file.seek(0)
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Could not decode image'}), 400

        extracted_urls = set()
        
        # Try pyzbar first (if available and arch matches)
        if PYZBAR_AVAILABLE:
            try:
                decoded_objects = decode(img)
                for obj in decoded_objects:
                    text = obj.data.decode('utf-8')
                    if text:
                        extracted_urls.add(text)
            except Exception:
                pass

        # Fallback to Robust OpenCV
        if not extracted_urls:
            detector_cv = cv2.QRCodeDetector()
            
            def detect_on_img(image):
                # Try Multi
                retval, decoded_info, points, _ = detector_cv.detectAndDecodeMulti(image)
                if retval:
                    for info in decoded_info:
                        if info: extracted_urls.add(info)
                # Try Single
                data, _, _ = detector_cv.detectAndDecode(image)
                if data: extracted_urls.add(data)

            # 1. Original
            detect_on_img(img)

            # 2. Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            detect_on_img(gray)
            
            # 3. Enhanced Contrast (CLAHE) - Excellent for lighting issues
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            detect_on_img(enhanced)
            
            # 4. Binary Threshold checks
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            detect_on_img(binary)
            
            # 5. Adaptive Threshold
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            detect_on_img(adaptive)
            
            # 6. Sharpening
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(gray, -1, kernel)
            detect_on_img(sharpened)
            
            # 7. Inverted (Negative)
            inverted = cv2.bitwise_not(gray)
            detect_on_img(inverted)

        extracted_data = []
        for url in extracted_urls:
            analysis = detector.predict(url)
            extracted_data.append({
                'content': url,
                'analysis': analysis
            })
            
        if not extracted_data:
            return jsonify({'error': 'No QR code detected. Try cropping the QR code closer or improving lighting.'}), 400
            
        return jsonify({'results': extracted_data})
        
    except Exception as e:
        print(f"Error processing QR: {e}")
        return jsonify({'error': 'Server error processing image'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
