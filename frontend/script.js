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

// 1. Trigger File Upload
uploadBox.addEventListener('click', () => fileInput.click());

// 2. Handle File Selection
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Show Image Preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            startAnalysis(file); // Start the API call immediately
        };
        reader.readAsDataURL(file);
    }
});

// 3. Connect to Backend & Analyze
async function startAnalysis(file) {
    // --- UI Update: Show Scanning Mode ---
    uploadBox.style.display = 'none';
    previewBox.style.display = 'block';
    introText.style.display = 'none';
    analysisPanel.style.display = 'block';
    
    scannerOverlay.style.display = 'block'; // Laser animation
    loadingState.style.display = 'block';   // "Extracting Features..." text
    resultState.style.display = 'none';     // Hide old results

    // --- Prepare Data for API ---
    const formData = new FormData();
    formData.append("file", file); // 'file' must match the parameter in FastAPI

    try {
        // --- API CALL ---
        // Ensure your backend is running on port 8000
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Expected Data: { result: "Cancer Positive", confidence: 98.5, raw_label: "LABEL_1" }
        displayResult(data);

    } catch (error) {
        console.error("Analysis failed:", error);
        alert("❌ Error: Could not connect to the AI Server.\nMake sure uvicorn is running!");
        resetUI();
    }
}

// 4. Display Results
function displayResult(data) {
    // Stop Loading Animations
    scannerOverlay.style.display = 'none';
    loadingState.style.display = 'none';
    resultState.style.display = 'block';

    // Reset Color Classes
    resultContainer.classList.remove('is-danger', 'is-safe');

    // Check Logic: "Positive" = Danger, "Negative" = Safe
    const isCancer = data.result.toLowerCase().includes("positive");

    if (isCancer) {
        // --- CANCER DETECTED ---
        resultContainer.classList.add('is-danger');
        resultTitle.innerText = "POSITIVE";
        resultDesc.innerText = "Potential malignancy detected. Immediate clinical consultation recommended.";
    } else {
        // --- HEALTHY / NEGATIVE ---
        resultContainer.classList.add('is-safe');
        resultTitle.innerText = "NEGATIVE";
        resultDesc.innerText = "No malignant features detected. Tissue appears normal.";
    }

    // Set Confidence
    confidenceValue.innerText = data.confidence + "%";
}

// 5. Reset App
function resetUI() {
    fileInput.value = '';
    previewBox.style.display = 'none';
    uploadBox.style.display = 'flex';
    
    analysisPanel.style.display = 'none';
    introText.style.display = 'block';
    
    // Clean up classes
    resultContainer.classList.remove('is-danger', 'is-safe');
}