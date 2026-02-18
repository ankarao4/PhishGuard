# PhishGuard - Phishing URL & QR Code Detector

A modern, high-performance web application to detect phishing attempts in URLs and QR codes using Machine Learning.

## Features

- **URL Analysis**: Uses a Machine Learning model (Random Forest logic) to detect suspicious patterns in URLs.
- **QR Code Scanning**: Upload QR code images to extract and analyze the embedded URL.
- **Modern Design**: Sleek Green & Black "Hacker" theme with glassmorphism effects.
- **Responsive**: Fully mobile-friendly layout.
- **Privacy Focused**: No personal data is stored.

## Tech Stack

- **Backend**: Python 3, Flask
- **Machine Learning**: Scikit-Learn, Pandas, NumPy
- **Image Processing**: OpenCV (headless)
- **Frontend**: HTML5, Vanilla CSS3, Vanilla JavaScript

## Setup & Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    python3 app.py
    ```

3.  **Access**:
    Open your browser and navigate to `http://localhost:3000`.

## Directory Structure

- `app.py`: Main Flask application.
- `model.py`: User-simulation ML Model logic.
- `templates/index.html`: Main One-Page frontend.
- `static/css/style.css`: Styling.
- `static/js/script.js`: Interactive frontend logic.
