# Phishing URL & QR Code Detector (PhishGuard)

A modern, machine learning-powered web application to detect phishing URLs and malicious QR codes.

## Features
- **URL Scanner**: Enter a URL to check if it's phishing or legitimate.
- **QR Code Decoder**: 
    - **Use Camera**: Scan QR codes directly using your device's camera.
    - **Upload Image**: Drag & drop or upload an image containing a QR code.
- **Mobile Responsive**: Works on desktops, laptops, and mobile phones.
- **Real-time Analysis**: Provides instant feedback with a confidence score.

## How to Run Locally

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ankarao4/PhishGuard.git
    cd PhishGuard
    ```

2.  **Install Dependencies**:
    Make sure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python3 app.py
    ```

4.  **Access the Website**:
    - Open your browser and go to: [http://localhost:3000](http://localhost:3000)
    - To access from your **mobile phone** on the same Wi-Fi:
        - Find your computer's local IP address (e.g., `192.168.1.5`).
        - On your phone, visit: `http://192.168.1.5:3000` (Replace with your actual IP).

## Deployment

To deploy this application to the web so anyone can access it, you can use services like **Render**, **Heroku**, or **PythonAnywhere**.

### Example: Deploying to Render
1. Create a [Render](https://render.com) account.
2. Click "New +" -> "Web Service".
3. Connect your GitHub repository (`ankarao4/PhishGuard`).
4. Set the following:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (You may need to add `gunicorn` to `requirements.txt`)
5. Click **Create Web Service**. Render will generate a public link for your website.

**Note**: Since this app uses a camera, accessing it via a public link (not localhost) usually requires **HTTPS** for browser permissions. Most cloud providers (like Render) provide HTTPS automatically.
