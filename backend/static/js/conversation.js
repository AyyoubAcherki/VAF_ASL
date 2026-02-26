// ===== CONVERSATION BRIDGE LOGIC =====

const chatMessages = document.getElementById('chatMessages');
const btnSigner = document.getElementById('btnSigner');
const btnSpeaker = document.getElementById('btnSpeaker');
const webcam = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const signProgressBar = document.getElementById('signProgressBar');
const vocalStatus = document.getElementById('vocalStatus');
const typingIndicator = document.getElementById('typingIndicator');
const p1Status = document.getElementById('p1-status').querySelector('.status-dot');
const p2Status = document.getElementById('p2-status').querySelector('.status-dot');
const micVisualizer = document.getElementById('micVisualizer');

// Avatar Elements
const systemSignerContainer = document.getElementById('systemSignerContainer');
const avatar3DContainer = document.getElementById('avatar3DContainer');
const signVideoPlayer = document.getElementById('signVideoPlayer');
const proAvatarImg = document.getElementById('proAvatarImg');
const signBadgeContainer = document.getElementById('signBadgeContainer');
const currentSignName = document.getElementById('currentSignName');
const animationProgress = document.getElementById('animationProgress');

// State
let isSignerActive = false;
let isSpeakerActive = false;

// Streams
let videoStream = null;
let audioStream = null;

// Vocal Logic
let mediaRecorder = null;
let audioChunks = [];
let voiceCheckInterval = null;

// Audio Visualizer
let audioContext = null;
let analyser = null;
let microphone = null;
let visualizerFrameId = null;

// Sign Logic
let frameBuffer = [];
const MAX_FRAMES = 40;
const WINDOW_STRIDE = 10;
let frameCounter = 0;
let signInterval = null;

// Avatar Logic
let videoQueue = [];
let isPlayingSequence = false;
let animationTimeouts = [];

// ===== TOGGLE FUNCTIONS =====

async function toggleSignerMode() {
    if (isSignerActive) {
        stopSignerMode();
    } else {
        await startSignerMode();
    }
}

async function toggleSpeakerMode() {
    if (isSpeakerActive) {
        stopSpeakerMode();
    } else {
        await startSpeakerMode();
    }
}

// ===== SIGNER MODE (WEBCAM) =====

async function startSignerMode() {
    try {
        closeAvatarView(); // Ensure avatar is hidden
        // If Speaker is active, stop it? Or allow both? 
        // User said "si le personne seign... click... si le personne normal... click..."
        // Typically implies mutual exclusion or dedicated turn-taking, but let's allow overlapping if hardware permits,
        // OR safer: stop audio if video starts to prevent resource conflict if single device?
        // Let's keep them independent for now.

        videoStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 320, height: 240, frameRate: 15 },
            audio: false // Only video
        });

        webcam.srcObject = videoStream;
        webcam.onloadedmetadata = () => webcam.play();

        isSignerActive = true;
        updateSignerUI(true);

        startSignLoop();

    } catch (error) {
        console.error("Camera Error:", error);
        alert("Impossible d'accéder à la caméra.");
    }
}

function stopSignerMode() {
    isSignerActive = false;
    updateSignerUI(false);

    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    webcam.srcObject = null;
    stopSignLoop();
}

function updateSignerUI(active) {
    const badge = document.getElementById('fluxStatusBadge');
    if (active) {
        btnSigner.innerHTML = '<i class="fas fa-stop"></i> <span>Arrêter Caméra</span>';
        btnSigner.style.backgroundColor = '#d32f2f'; // Red for stop
        p2Status.className = 'status-dot status-active';
        if (badge) { badge.textContent = "DIRECT"; badge.style.background = "#d32f2f"; badge.style.color = "white"; }
    } else {
        btnSigner.innerHTML = '<i class="fas fa-video"></i> <span>Activer Caméra (Signer)</span>';
        btnSigner.style.backgroundColor = '#00a884'; // Original Green
        p2Status.className = 'status-dot status-inactive';
        if (badge) { badge.textContent = "AVATAR"; badge.style.background = "#00a884"; badge.style.color = "white"; }
    }
}

// ===== SPEAKER MODE (MICROPHONE) =====

async function startSpeakerMode() {
    try {
        audioStream = await navigator.mediaDevices.getUserMedia({
            video: false,
            audio: true
        });

        isSpeakerActive = true;
        updateSpeakerUI(true);

        setupAudioVisualizer(audioStream);
        startVocalLoop();

    } catch (error) {
        console.error("Mic Error:", error);
        alert("Impossible d'accéder au microphone.");
    }
}

function stopSpeakerMode() {
    isSpeakerActive = false;
    updateSpeakerUI(false);

    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }

    stopAudioVisualizer();
    stopVocalLoop();
}

function updateSpeakerUI(active) {
    if (active) {
        btnSpeaker.innerHTML = '<i class="fas fa-stop"></i> <span>Arrêter Micro</span>';
        btnSpeaker.style.backgroundColor = '#d32f2f'; // Red for stop
        p1Status.className = 'status-dot status-active';
    } else {
        btnSpeaker.innerHTML = '<i class="fas fa-microphone"></i> <span>Activer Micro (Parler)</span>';
        btnSpeaker.style.backgroundColor = '#008fcc'; // Blue
        p1Status.className = 'status-dot status-inactive';
    }
}

// ===== LOGIC LOOPS =====

function startVocalLoop() {
    vocalStatus.textContent = 'Écoute en cours...';
    startRecording();
}

function stopVocalLoop() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    if (voiceCheckInterval) clearInterval(voiceCheckInterval);
    vocalStatus.textContent = 'Microphone inactif';
}

function startRecording() {
    if (!isSpeakerActive || !audioStream) return;

    audioChunks = [];
    try {
        mediaRecorder = new MediaRecorder(audioStream);
    } catch (e) { console.error(e); return; }

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
        if (audioChunks.length > 0 && isSpeakerActive) {
            await processVocalChunk();
        }
        if (isSpeakerActive) startRecording();
    };

    mediaRecorder.start();

    // Segment every 4-5 seconds
    voiceCheckInterval = setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
    }, 4500);
}

// Using Enhanced Audio Translation API (Text + Signs)
async function processVocalChunk() {
    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    if (blob.size < 1000) return; // Silence

    const fd = new FormData();
    fd.append('audio', blob, 'audio.webm');

    vocalStatus.textContent = 'Analyse...';
    vocalStatus.style.color = '#FFA000'; // Orange while processing

    try {
        const res = await fetch('/api/audio/translate/asl', { method: 'POST', body: fd });
        const data = await res.json();

        console.log("Audio API Response:", data);

        if (data.error) {
            console.error("Audio API Error:", data.error);
            vocalStatus.textContent = "Erreur: " + data.error;
            vocalStatus.style.color = 'red';
            // Show brief toast/message?
            setTimeout(() => { if (isSpeakerActive) vocalStatus.textContent = 'Écoute en cours...'; }, 2000);
            return;
        }

        if (data.text && data.text.trim().length > 0) {
            addMessage('Vocal', data.text, 'vocal');

            // Check if signs are available to animate
            if (data.asl_sequence && data.asl_sequence.length > 0) {
                console.log("Signs received:", data.asl_sequence);
                animateSigns(data.asl_sequence);
            }
        } else {
            vocalStatus.textContent = "Je n'ai rien entendu...";
            setTimeout(() => { if (isSpeakerActive) vocalStatus.textContent = 'Écoute en cours...'; }, 2000);
        }
    } catch (e) {
        console.error("Fetch Error:", e);
        vocalStatus.textContent = "Erreur réseau";
    }
    finally {
        if (isSpeakerActive && vocalStatus.textContent === 'Analyse...') {
            vocalStatus.textContent = 'Écoute en cours...';
            vocalStatus.style.color = '#666';
        }
    }
}

function startSignLoop() {
    frameBuffer = [];
    frameCounter = 0;
    if (signInterval) clearInterval(signInterval);

    signInterval = setInterval(async () => {
        if (!isSignerActive) return;

        try {
            canvas.width = 64; canvas.height = 64;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(webcam, 0, 0, 64, 64);
            const frame = canvas.toDataURL('image/jpeg', 0.6);

            frameBuffer.push(frame);
            if (frameBuffer.length > MAX_FRAMES) frameBuffer.shift();

            frameCounter++;
            signProgressBar.style.width = `${(frameBuffer.length / MAX_FRAMES) * 100}%`;

            if (frameCounter >= WINDOW_STRIDE && frameBuffer.length === MAX_FRAMES) {
                frameCounter = 0;
                await processSignSequence();
            }
        } catch (e) { console.error(e); }
    }, 100);
}

function stopSignLoop() {
    if (signInterval) clearInterval(signInterval);
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) typingIndicator.style.display = 'none';
    signProgressBar.style.width = '0%';
}

async function processSignSequence() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) typingIndicator.style.display = 'block';

    // Copy buffer to avoid modification during async call
    const toSend = [...frameBuffer];

    try {
        // Ensure endpoint matches
        const res = await fetch('/api/predict_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frames: toSend })
        });

        // Wait, did I use 'predict_video' or 'predict_video_sequence'? 
        // Checking routes.py via grep showed predict_video... let me re-verify route name in next step if this fails.
        // Assuming /api/predict_video based on previous code.

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        const data = await res.json();
        console.log("Sign Prediction:", data);

        // Lower threshold to 0.5 for testing
        if (data.confidence > 0.5 && data.word) {
            if (data.word.startsWith('Unknown')) {
                // Optional: Show "..." for trying to understand?
                // For now, ignore to keep chat clean unless explicitly debugging
                console.log("Ignored Unknown:", data.word);
            } else {
                addMessage('Signeur', data.word, 'signer');
                // Clear buffer after successful detection to avoid repeating
                frameBuffer = [];
                // Reset progress bar visual
                signProgressBar.style.width = '0%';
            }
        }
    } catch (e) {
        console.error("Sign Prediction Error:", e);
    }
    finally {
        if (typingIndicator) typingIndicator.style.display = 'none';
    }
}

function setupAudioVisualizer(stream) {
    if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    microphone = audioContext.createMediaStreamSource(stream);
    microphone.connect(analyser);
    analyser.fftSize = 256;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const bars = micVisualizer.querySelectorAll('.bar');

    function animate() {
        if (!isSpeakerActive) return;
        analyser.getByteFrequencyData(dataArray);
        const step = Math.floor(bufferLength / 5);
        bars.forEach((bar, i) => {
            const h = Math.max(5, (dataArray[i * step] / 255) * 35);
            bar.style.height = `${h}px`;
        });
        visualizerFrameId = requestAnimationFrame(animate);
    }
    animate();
}

function stopAudioVisualizer() {
    if (visualizerFrameId) cancelAnimationFrame(visualizerFrameId);
    // don't close context to reuse it
}

// ===== AVATAR ANIMATION LOGIC =====

function animateSigns(signs) {
    openAvatarView();
    // Reset queue
    videoQueue = signs.map(s => typeof s === 'string' ? s : (s.asl_word || s)).filter(s => s);
    if (videoQueue.length > 0) {
        playNextVideo(0);
    } else {
        closeAvatarView();
    }
}

function openAvatarView() {
    systemSignerContainer.style.display = 'block';
    const badge = document.getElementById('fluxStatusBadge');
    if (badge) { badge.textContent = "IA ACTIVE"; badge.style.background = "#2196F3"; }

    // Initialize 3D if needed
    if (typeof initAvatarScene === 'function' && !window.avatarSceneInited) {
        initAvatarScene();
        window.avatarSceneInited = true;
    }
}

function closeAvatarView() {
    systemSignerContainer.style.display = 'none';
    isPlayingSequence = false;
    animationTimeouts.forEach(t => clearTimeout(t));
    if (signVideoPlayer) signVideoPlayer.pause();

    // Reset visual
    if (currentSignName) currentSignName.textContent = "Système";
    if (animationProgress) animationProgress.style.width = '0%';
    if (signBadgeContainer) signBadgeContainer.innerHTML = '';

    // Reset Badge
    const badge = document.getElementById('fluxStatusBadge');
    if (badge) {
        if (isSignerActive) {
            badge.textContent = "DIRECT"; badge.style.background = "#d32f2f";
        } else {
            badge.textContent = "INACTIF"; badge.style.background = "rgba(0,0,0,0.2)";
        }
    }
}

function playNextVideo(index) {
    if (index >= videoQueue.length) {
        // Finished
        setTimeout(closeAvatarView, 2000); // Wait 2s then close
        return;
    }

    const word = videoQueue[index];
    isPlayingSequence = true;

    if (animationProgress) {
        animationProgress.style.width = `${((index) / videoQueue.length) * 100}%`;
    }
    if (currentSignName) currentSignName.textContent = `Signe: ${word}`;

    // Show Badge
    const badge = document.createElement('div');
    badge.className = 'sign-badge';
    badge.textContent = word;
    badge.style.cssText = 'background: rgba(0,168,132,0.9); color: white; padding: 10px 20px; border-radius: 20px; font-size: 24px; font-weight: bold; border: 2px solid white; animation: popIn 0.3s ease;';

    if (signBadgeContainer) {
        signBadgeContainer.innerHTML = '';
        signBadgeContainer.appendChild(badge);
    }

    // 1. Try 3D
    const known3DSigns = ['HELLO', 'GOOD_MORNING', 'THANKS', 'PLEASE', 'YES', 'NO', 'I', 'YOU', '21'];

    if (known3DSigns.includes(word.toUpperCase()) && typeof playASLAnimation === 'function') {
        avatar3DContainer.style.display = 'block';
        signVideoPlayer.style.display = 'none';
        proAvatarImg.style.display = 'none';

        playASLAnimation(word).then(() => {
            setTimeout(() => playNextVideo(index + 1), 500);
        });
        return;
    }

    // 2. Fallback to Video
    const videoUrl = `/api/video/${encodeURIComponent(word)}`;

    avatar3DContainer.style.display = 'none';
    signVideoPlayer.style.display = 'block';
    proAvatarImg.style.display = 'none';

    signVideoPlayer.src = videoUrl;
    signVideoPlayer.load();

    const onCanPlay = () => signVideoPlayer.play().catch(e => handleError());
    const onEnded = () => {
        cleanup();
        setTimeout(() => playNextVideo(index + 1), 300);
    };
    const handleError = () => {
        console.warn(`Video missing for ${word}`);
        cleanup();
        // Fallback to image + badge delay
        signVideoPlayer.style.display = 'none';
        proAvatarImg.style.display = 'block';
        setTimeout(() => playNextVideo(index + 1), 1500);
    };

    function cleanup() {
        signVideoPlayer.removeEventListener('canplay', onCanPlay);
        signVideoPlayer.removeEventListener('ended', onEnded);
        signVideoPlayer.removeEventListener('error', handleError);
    }

    signVideoPlayer.addEventListener('canplay', onCanPlay, { once: true });
    signVideoPlayer.addEventListener('ended', onEnded, { once: true });
    signVideoPlayer.addEventListener('error', handleError, { once: true });
}

// --- UI HELPERS ---
function addMessage(sender, text, type) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // WhatsApp style structure
    // Sender name is hidden via CSS for clean look, but we can keep it in DOM or remove it.
    // Let's keep it minimal: Content + Time

    // Add checkmark for 'vocal' (My messages)
    let statusIcon = '';
    if (type === 'vocal') {
        statusIcon = '<span style="color: #53bdeb; margin-left: 3px;">✓✓</span>';
    }

    msgDiv.innerHTML = `
        <div class="message-content" style="margin-bottom: 0;">${text}</div>
        <div class="message-info">${time} ${statusIcon}</div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function clearChat() {
    chatMessages.innerHTML = '';
}
