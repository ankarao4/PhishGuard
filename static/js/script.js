document.addEventListener('DOMContentLoaded', () => {
    // Initial setup if needed
    console.log("PhishGuard Loaded");
    
    // Tab Switching Logic
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            const target = tab.getAttribute('onclick').replace("openTab('", "").replace("')", "");
            document.getElementById(target).classList.add('active');
        });
    });

    // Drag and Drop for QR
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('qrInput');

    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('active');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('active');
    });

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('active');
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });
});

async function scanURL() {
    const urlInput = document.getElementById('urlInput').value;
    const resultBox = document.getElementById('url-result');
    
    if (!urlInput) {
        alert("Please enter a URL");
        return;
    }

    resultBox.innerHTML = '<div class="loader">Scanning...</div>';
    resultBox.classList.remove('hidden');

    try {
        const response = await fetch('/predict-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: urlInput }),
        });

        const data = await response.json();
        displayResult(data, resultBox);
    } catch (error) {
        resultBox.innerHTML = `<span class="error">Error: ${error.message}</span>`;
    }
}

async function handleFile(file) {
    const resultBox = document.getElementById('qr-result');
    if (!file) return;

    resultBox.innerHTML = '<div class="loader">Decoding & Analyzing...</div>';
    resultBox.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/analyze-qr', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();
        if (data.error) {
            resultBox.innerHTML = `<span class="error">${data.error}</span>`;
        } else {
             // For QR, it returns an array of results usually, 
             // but our backend returns {results: [...]}
             if(data.results && data.results.length > 0) {
                 // Just show the first one for simplicity
                 const firstResult = data.results[0]; 
                 // It contains {content: "url", analysis: { ... }}
                 let displayData = firstResult.analysis;
                 displayData.scanned_content = firstResult.content;
                 displayResult(displayData, resultBox);
             } else {
                 resultBox.innerHTML = "No analyzing data found.";
             }
        }
    } catch (error) {
        resultBox.innerHTML = `<span class="error">Error: ${error.message}</span>`;
    }
}

function displayResult(data, container) {
    const isPhishing = data.is_phishing;
    const colorClass = isPhishing ? 'danger' : 'safe';
    const icon = isPhishing ? 'fa-exclamation-triangle' : 'fa-check-circle';
    
    let html = `
        <div class="result-card ${colorClass}">
            <div class="icon-wrapper">
                <i class="fas ${icon}"></i>
            </div>
            <h3>${data.verdict}</h3>
            <p class="url-display">${data.url || data.scanned_content}</p>
            <div class="score-bar">
                <div class="score-fill" style="width: ${data.risk_score}%"></div>
            </div>
            <p>Risk Score: <strong>${data.risk_score}/100</strong></p>
            <ul class="details-list">
                ${data.details.map(d => `<li>${d}</li>`).join('')}
            </ul>
        </div>
    `;
    container.innerHTML = html;
}
