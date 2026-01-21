const fileInput = document.getElementById('fileInput');
const uploadBox = document.getElementById('uploadBox');
const previewBox = document.getElementById('previewBox');
const imagePreview = document.getElementById('imagePreview');
const scannerOverlay = document.getElementById('scannerOverlay');

const introText = document.getElementById('introText');
const analysisPanel = document.getElementById('analysisPanel');
const loadingState = document.getElementById('loadingState');
const resultState = document.getElementById('resultState');

const resultTitle = document.getElementById('resultTitle');
const resultDesc = document.getElementById('resultDesc');
const confidenceValue = document.getElementById('confidenceValue');
const resultContainer = document.querySelector('.result-state');

// Trigger upload
uploadBox.addEventListener('click', () => fileInput.click());

// Handle file
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            startAnalysis();
        };
        reader.readAsDataURL(file);
    }
});

function startAnalysis() {
    // 1. Switch UI to Scan Mode
    uploadBox.style.display = 'none';
    previewBox.style.display = 'block';
    introText.style.display = 'none';
    analysisPanel.style.display = 'block';
    
    // 2. Start Animations
    scannerOverlay.style.display = 'block'; // Laser effect on image
    loadingState.style.display = 'block';
    resultState.style.display = 'none';

    // 3. Simulate Backend Delay (3 seconds)
    setTimeout(() => {
        showResults();
    }, 3000);
}

function showResults() {
    // Stop animations
    scannerOverlay.style.display = 'none';
    loadingState.style.display = 'none';
    resultState.style.display = 'block';

    // Randomize Logic (For Demo)
    const isPositive = Math.random() > 0.5;
    const confidence = (Math.random() * (99 - 85) + 85).toFixed(1);

    resultContainer.classList.remove('is-danger', 'is-safe');

    if (isPositive) {
        // Cancer Detected Case
        resultContainer.classList.add('is-danger');
        resultTitle.innerText = "DETECTED";
        resultDesc.innerText = "Malignant cell patterns identified.";
        confidenceValue.innerText = confidence + "%";
    } else {
        // Healthy Case
        resultContainer.classList.add('is-safe');
        resultTitle.innerText = "NEGATIVE";
        resultDesc.innerText = "Tissue analysis within normal limits.";
        confidenceValue.innerText = confidence + "%";
    }
}

function resetUI() {
    fileInput.value = '';
    previewBox.style.display = 'none';
    uploadBox.style.display = 'flex';
    
    analysisPanel.style.display = 'none';
    introText.style.display = 'block';
    
    // Reset classes
    resultContainer.classList.remove('is-danger', 'is-safe');
}