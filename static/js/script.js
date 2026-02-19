document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching
    const tabs = document.querySelectorAll('.tab-btn');
    const sections = {
        'url-tab': document.getElementById('url-section'),
        'qr-tab': document.getElementById('qr-section')
    };

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Hide all sections, show target
            Object.values(sections).forEach(s => s.style.display = 'none');
            const targetId = tab.id.replace('-tab', '-section');
            document.getElementById(targetId).style.display = 'block';

            // Clear results
            hideResult();
        });
    });

    // URL Form Submission
    const urlForm = document.getElementById('url-form');
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const urlInput = document.getElementById('url-input').value;
        if (!urlInput) return;
        analyzeUrl(urlInput);
    });

    // QR Code Scanning (Camera)
    const startScanBtn = document.getElementById('start-scan-btn');
    const readerDiv = document.getElementById('reader');
    let html5QrCode;

    startScanBtn.addEventListener('click', () => {
        if (!html5QrCode) {
            html5QrCode = new Html5Qrcode("reader");
        }

        readerDiv.style.display = 'block';
        startScanBtn.style.display = 'none';

        const config = { fps: 10, qrbox: { width: 250, height: 250 } };

        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess, onScanFailure)
            .catch(err => {
                console.error(err);
                displayError("Error starting camera: " + err);
                readerDiv.style.display = 'none';
                startScanBtn.style.display = 'block';
            });
    });

    async function onScanSuccess(decodedText, decodedResult) {
        // Stop scanning after success
        if (html5QrCode) {
            await html5QrCode.stop();
            readerDiv.style.display = 'none';
            startScanBtn.style.display = 'block';
        }

        // Analyze the URL found in QR
        analyzeUrl(decodedText);
    }

    function onScanFailure(error) {
        // handle scan failure, usually better to ignore and keep scanning.
        // console.warn(`Code scan error = ${error}`);
    }

    // Helper to analyze URL (reused for both manual entry and QR scan)
    async function analyzeUrl(url) {
        showLoader();
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });
            const data = await response.json();
            displayResult(data);
        } catch (error) {
            displayError('An error occurred while analyzing the URL.');
        } finally {
            hideLoader();
        }
    }

    // QR Code Upload (File)
    const qrInput = document.getElementById('qr-input');
    const dropZone = document.getElementById('drop-zone');

    dropZone.addEventListener('click', () => qrInput.click());

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    qrInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        showLoader();
        try {
            const response = await fetch('/api/scan_qr', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            displayResult(data);
        } catch (error) {
            displayError('An error occurred while scanning the QR code.');
        } finally {
            hideLoader();
        }
    }

    // UI Helpers
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const resultTitle = document.getElementById('result-title');
    const resultText = document.getElementById('result-text');

    function showLoader() {
        loader.style.display = 'block';
        resultContainer.style.display = 'none';
    }

    function hideLoader() {
        loader.style.display = 'none';
    }

    function displayResult(data) {
        if (data.error) {
            displayError(data.error);
            return;
        }

        resultContainer.style.display = 'block';
        resultContainer.className = data.result === 'Legitimate' ? 'safe' : 'danger';

        const icon = data.result === 'Legitimate' ? '✔' : '⚠';
        resultTitle.textContent = `${icon} ${data.result.toUpperCase()}`;

        let html = `<p>Analyzed URL: <strong>${escapeHtml(data.url)}</strong></p>`;
        if (data.confidence) {
            html += `<p>Confidence Score: ${data.confidence}</p>`;
        }
        resultText.innerHTML = html;
    }

    function displayError(message) {
        resultContainer.style.display = 'block';
        resultContainer.className = 'danger';
        resultTitle.textContent = 'Error';
        resultText.textContent = message;
    }

    function hideResult() {
        resultContainer.style.display = 'none';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
