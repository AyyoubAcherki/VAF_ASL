// ===== PREDICT ONLINE PAGE (WEBCAM) =====
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const captureBtn = document.getElementById('captureBtn');
const webcam = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const currentSign = document.getElementById('currentSign');
const currentConfidence = document.getElementById('currentConfidence');
const confidenceBar = document.getElementById('confidenceBar');
const historyDisplay = document.getElementById('historyDisplay');
const liveIndicator = document.getElementById('liveIndicator');

// New UI elements
const captureProgressContainer = document.getElementById('captureProgressContainer');
const captureProgressBar = document.getElementById('captureProgressBar');
const progressPercentage = document.getElementById('progressPercentage');
const modeWordBtn = document.getElementById('modeWord');
const modePhraseBtn = document.getElementById('modePhrase');
const modeLiveBtn = document.getElementById('modeLive');

let stream = null;
let isPredicting = false;
let predictionInterval = null;
let predictionHistory = [];
let currentMode = 'word'; // 'word' or 'phrase' or 'live'

// Buffering for phrase/live mode
let frameBuffer = [];
const MAX_FRAMES = 40;
let isCapturingSequence = false;

function setMode(mode) {
    if (isCapturingSequence) return;

    currentMode = mode;

    // Reset UI active states
    [modeWordBtn, modePhraseBtn, modeLiveBtn].forEach(btn => btn.classList.remove('active'));

    if (mode === 'word') {
        modeWordBtn.classList.add('active');
        captureBtn.innerHTML = 'Capturer';
        if (liveIndicator) liveIndicator.style.display = 'none';
        stopLiveStream();
        if (stream && !isPredicting) startPrediction();
    } else if (mode === 'phrase') {
        modePhraseBtn.classList.add('active');
        captureBtn.innerHTML = 'Capturer Phrase (4s)';
        if (liveIndicator) liveIndicator.style.display = 'none';
        stopLiveStream();
        stopPrediction();
    } else if (mode === 'live') {
        modeLiveBtn.classList.add('active');
        captureBtn.innerHTML = 'Live en cours...';
        if (liveIndicator) liveIndicator.style.display = 'flex';
        stopPrediction();
        if (stream) startLiveStream();
    }
}

async function startWebcam() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 }
        });
        webcam.srcObject = stream;

        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        captureBtn.style.display = 'inline-block';

        if (currentMode === 'word') {
            startPrediction();
        } else if (currentMode === 'live') {
            startLiveStream();
        }
    } catch (error) {
        console.error('Error accessing webcam:', error);
        alert('Impossible d\'accéder à la webcam. Veuillez autoriser l\'accès à la caméra.');
    }
}

function stopWebcam() {
    stopPrediction();
    stopLiveStream();
    isCapturingSequence = false;

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    webcam.srcObject = null;
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
    captureBtn.style.display = 'none';
    if (captureProgressContainer) captureProgressContainer.style.display = 'none';

    // Réinitialiser l'affichage
    resetPredictionDisplay();
}

function resetPredictionDisplay() {
    if (currentSign) {
        const char = currentSign.querySelector('.sign-char');
        const label = currentSign.querySelector('.sign-label');
        if (char) char.textContent = '-';
        if (label) label.textContent = 'En attente...';
    }
    if (currentConfidence) currentConfidence.textContent = '0%';
    if (confidenceBar) confidenceBar.style.width = '0%';
}

function startPrediction() {
    if (isPredicting || currentMode !== 'word') return;

    isPredicting = true;
    predictionInterval = setInterval(async () => {
        await predictFrame();
    }, 1000); // 1s interval for stability in word mode
}

function stopPrediction() {
    if (predictionInterval) {
        clearInterval(predictionInterval);
        predictionInterval = null;
    }
    isPredicting = false;
}

// ===== LIVE STREAM MODE (CONTINUOUS) =====
let liveInterval = null;
let lastPredictedWord = '';

function startLiveStream() {
    if (liveInterval || currentMode !== 'live') return;

    frameBuffer = [];
    liveInterval = setInterval(async () => {
        if (!stream) return;

        // Capture frame for the CNN-LSTM rolling buffer
        canvas.width = 64;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(webcam, 0, 0, 64, 64);
        const frameData = canvas.toDataURL('image/jpeg', 0.5);

        frameBuffer.push(frameData);
        if (frameBuffer.length > MAX_FRAMES) {
            frameBuffer.shift();
        }

        // Process every 300ms (approx 3 frames at 10fps)
        if (frameBuffer.length === MAX_FRAMES && frameBuffer.length % 3 === 0) {
            await processLiveSequence();
        }
    }, 100);
}

function stopLiveStream() {
    if (liveInterval) {
        clearInterval(liveInterval);
        liveInterval = null;
    }
}

async function processLiveSequence() {
    try {
        const response = await fetch('/api/predict_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frames: frameBuffer,
                save: false
            })
        });

        const result = await response.json();

        if (result.confidence > 0.8 && result.word !== 'background') {
            updatePredictionDisplay(result);

            if (result.word !== lastPredictedWord) {
                lastPredictedWord = result.word;
                addToHistory(result, frameBuffer[MAX_FRAMES - 1]);
            }
        }
    } catch (e) {
        console.error('Live Stream Error:', e);
    }
}

async function predictFrame(save = false) {
    if (!webcam.videoWidth || !webcam.videoHeight) return null;

    canvas.width = 160;
    canvas.height = 120;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg', 0.6);

    try {
        const response = await fetch('/api/predict_base64', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData, save: save })
        });

        const result = await response.json();
        if (response.ok) {
            updatePredictionDisplay(result);
            return result;
        }
    } catch (error) {
        console.error('Error predicting:', error);
    }
    return null;
}

function updatePredictionDisplay(result) {
    const signChar = currentSign.querySelector('.sign-char');
    const signLabel = currentSign.querySelector('.sign-label');

    const label = result.class || result.word || '-';
    const conf = result.confidence || 0;

    if (signChar) signChar.textContent = label;
    if (signLabel) signLabel.textContent = label === '-' ? 'En attente...' : label;
    if (currentConfidence) currentConfidence.textContent = (conf * 100).toFixed(1) + '%';
    if (confidenceBar) confidenceBar.style.width = (conf * 100) + '%';

    if (signChar) {
        if (conf > 0.7) {
            signChar.style.color = '#4CAF50';
        } else if (conf > 0.4) {
            signChar.style.color = '#FF9800';
        } else {
            signChar.style.color = '#666';
        }
    }
}

async function captureFrame() {
    if (currentMode === 'word') {
        const result = await predictFrame(true);
        if (result) {
            addToHistory(result, canvas.toDataURL('image/jpeg', 0.8));
        }
    } else if (currentMode === 'phrase') {
        captureSequence();
    }
}

async function captureSequence() {
    if (isCapturingSequence || !stream) return;

    isCapturingSequence = true;
    frameBuffer = [];
    if (captureProgressContainer) captureProgressContainer.style.display = 'block';
    resetPredictionDisplay();

    let framesCollected = 0;
    const timer = setInterval(async () => {
        if (framesCollected >= MAX_FRAMES) {
            clearInterval(timer);
            await sendSequence();
            return;
        }

        canvas.width = 64;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(webcam, 0, 0, 64, 64);

        frameBuffer.push(canvas.toDataURL('image/jpeg', 0.5));
        framesCollected++;

        const percent = Math.round((framesCollected / MAX_FRAMES) * 100);
        if (captureProgressBar) captureProgressBar.style.width = percent + '%';
        if (progressPercentage) progressPercentage.textContent = percent + '%';

    }, 100);
}

async function sendSequence() {
    if (progressPercentage) progressPercentage.textContent = 'Analyse...';
    if (captureProgressBar) captureProgressBar.style.background = '#FF9800';

    try {
        const response = await fetch('/api/predict_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frames: frameBuffer,
                save: true
            })
        });

        const result = await response.json();

        if (response.ok) {
            updatePredictionDisplay(result);
            addToHistory(result, frameBuffer[Math.floor(MAX_FRAMES / 2)]);
        } else {
            alert('Erreur: ' + (result.error || 'Erreur lors de l\'analyse'));
        }
    } catch (error) {
        console.error('Error sending sequence:', error);
    } finally {
        isCapturingSequence = false;
        if (captureProgressContainer) captureProgressContainer.style.display = 'none';
        if (captureProgressBar) {
            captureProgressBar.style.width = '0%';
            captureProgressBar.style.background = '#4CAF50';
        }
    }
}

function addToHistory(result, imageData) {
    const label = result.class || result.word;
    const historyItem = {
        class: label,
        confidence: result.confidence,
        image: imageData,
        timestamp: new Date().toLocaleTimeString()
    };

    predictionHistory.push(historyItem);
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    if (!historyDisplay) return;

    if (predictionHistory.length === 0) {
        historyDisplay.innerHTML = '<p class="empty-history" style="color: #666; font-style: italic; text-align: center; padding: 20px;">Aucune prédiction enregistrée</p>';
        return;
    }

    historyDisplay.innerHTML = '';
    predictionHistory.slice(-10).reverse().forEach((item) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="${item.image}" alt="${item.class}" style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover; border: 1px solid rgba(255,255,255,0.1);">
                <div style="flex-grow: 1;">
                    <div style="font-weight: 600; color: #4CAF50; font-size: 1.1rem;">${item.class}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                        <span style="font-size: 0.8rem; color: #888;">${item.timestamp}</span>
                        <span style="font-size: 0.85rem; color: #2196F3; font-weight: bold;">${(item.confidence * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        `;
        historyDisplay.appendChild(historyItem);
    });
}

function clearHistory() {
    predictionHistory = [];
    updateHistoryDisplay();
}

window.addEventListener('beforeunload', () => {
    stopWebcam();
});

// ===== OLLAMA INTEGRATION =====
async function translateSentence() {
    if (predictionHistory.length === 0) {
        alert("Aucun mot à traduire. Veuillez signer d'abord.");
        return;
    }

    const words = predictionHistory.map(item => item.class);
    const resultDiv = document.getElementById('sentenceResult');
    const textP = document.getElementById('translatedText');

    // UI Loading state
    if (resultDiv) resultDiv.style.display = 'block';
    if (textP) textP.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traduction en cours...';

    try {
        const response = await fetch('/api/gloss_to_sentence', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                words: words,
                lang: 'fr' // Ou récupérer la langue depuis l'interface si multilingue
            })
        });

        const data = await response.json();

        if (data.sentence) {
            if (textP) textP.textContent = data.sentence;
        } else {
            if (textP) textP.textContent = "Erreur de traduction.";
        }
    } catch (error) {
        console.error('Erreur traduction:', error);
        if (textP) textP.textContent = "Erreur de connexion au service de traduction.";
    }
}
