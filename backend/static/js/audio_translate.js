// ===== AUDIO TRANSLATE PAGE =====
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentAudioBlob = null;

function switchTab(tab) {
    // Masquer tous les onglets
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Masquer tous les boutons d'onglet
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Afficher l'onglet sélectionné
    if (tab === 'record') {
        document.getElementById('recordTab').classList.add('active');
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
    } else {
        document.getElementById('uploadTab').classList.add('active');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        // Détecter le format supporté par le navigateur
        let mimeType = 'audio/webm';
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
            mimeType = 'audio/webm';
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
            mimeType = 'audio/ogg;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
            mimeType = 'audio/mp4';
        } else if (MediaRecorder.isTypeSupported('audio/wav')) {
            mimeType = 'audio/wav';
        }

        mediaRecorder = new MediaRecorder(stream, { mimeType: mimeType });
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            // Créer un Blob avec le type MIME détecté
            currentAudioBlob = new Blob(audioChunks, { type: mimeType });
            document.getElementById('translateBtn').style.display = 'inline-block';
            document.getElementById('recordingStatus').textContent = `Enregistrement terminé (${(currentAudioBlob.size / 1024).toFixed(2)} KB)`;
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start(100); // Enregistrer par chunks de 100ms
        isRecording = true;

        document.getElementById('recordBtn').style.display = 'none';
        document.getElementById('stopRecordBtn').style.display = 'inline-block';
        document.getElementById('recordingStatus').textContent = 'Enregistrement en cours...';
        document.getElementById('recordingStatus').classList.add('recording');
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Impossible d\'accéder au microphone. Veuillez autoriser l\'accès.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;

        document.getElementById('recordBtn').style.display = 'inline-block';
        document.getElementById('stopRecordBtn').style.display = 'none';
        document.getElementById('recordingStatus').textContent = 'Enregistrement terminé';
        document.getElementById('recordingStatus').classList.remove('recording');
    }
}

// Gérer l'upload de fichier audio
document.getElementById('audioInput').addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        currentAudioBlob = e.target.files[0];
        document.getElementById('fileInfo').textContent = `Fichier: ${e.target.files[0].name}`;
        document.getElementById('translateBtn').style.display = 'inline-block';
    }
});

async function translateAudio() {
    if (!currentAudioBlob) {
        alert('Veuillez enregistrer ou uploader un fichier audio');
        return;
    }

    // Afficher le loading
    const transcribedText = document.getElementById('transcribedText');
    transcribedText.innerHTML = '<p class="placeholder">Traduction en cours...<br><small>Audio → Texte → ASL</small></p>';

    // Préparer le formulaire
    const formData = new FormData();
    formData.append('audio', currentAudioBlob);

    try {
        // Utiliser le nouveau endpoint audio-to-ASL
        const response = await fetch('/api/audio/translate/asl', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            let errorMsg = result.error || 'Erreur lors de la traduction';

            // Afficher les suggestions si disponibles
            if (result.suggestions) {
                errorMsg += '<br><br><strong>Suggestions:</strong><ul>';
                result.suggestions.forEach(s => {
                    errorMsg += `<li>${s}</li>`;
                });
                errorMsg += '</ul>';
            }

            transcribedText.innerHTML = `<p style="color: #dc3545; font-size: 1rem;">${errorMsg}</p>`;
            console.error('Erreur de traduction:', result);
            return;
        }

        // Afficher le texte transcrit avec la langue détectée
        const langEmoji = result.detected_language === 'fr' ? '🇫🇷' :
            result.detected_language === 'ar' ? '🇲🇦' : '🇺🇸';

        transcribedText.innerHTML = `
            <p style="font-size: 1.2rem; line-height: 1.8;">
                ${langEmoji} ${result.text}
            </p>
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <small style="color: #888;">
                    <strong>Statistiques:</strong> 
                    ${result.total_words} mots | 
                    ${result.found_words} trouvés | 
                    ${result.unknown_words} inconnus
                </small>
            </div>
        `;

        // Afficher les prédictions ASL
        if (result.asl_predictions && result.asl_predictions.length > 0) {
            displayASLPredictions(result.asl_predictions);

            if (result.asl_sequence && result.asl_sequence.length > 0) {
                animateSigns(result.asl_sequence);
            }

            // Sauvegarder dans l'historique
            saveToHistory(result.text);

            // Afficher le bouton d'entraînement
            const saveTrainingBtn = document.getElementById('saveTrainingBtn');
            if (saveTrainingBtn) {
                saveTrainingBtn.style.display = 'inline-block';
                saveTrainingBtn.setAttribute('data-text', result.text);
            }
        }
    } catch (error) {
        console.error('Error translating audio:', error);
        transcribedText.innerHTML = `<p style="color: #dc3545;">Erreur: ${error.message}</p>`;
    }
}

function displayASLPredictions(predictions) {
    // Créer une section pour afficher les prédictions ASL
    let existingSection = document.getElementById('aslPredictionsSection');

    if (!existingSection) {
        existingSection = document.createElement('div');
        existingSection.id = 'aslPredictionsSection';
        existingSection.style.cssText = 'margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px;';

        const textResult = document.querySelector('.text-result');
        if (textResult) {
            textResult.appendChild(existingSection);
        } else {
            console.warn('.text-result element not found');
            return;
        }
    }

    let html = '<h4 style="margin-bottom: 15px; color: #4CAF50;">📊 Prédictions ASL</h4>';
    html += '<div style="display: grid; gap: 10px;">';

    predictions.forEach(pred => {
        if (pred.status === 'found' || pred.status === 'phrase_match') {
            const displayTitle = pred.status === 'phrase_match' ? 'Phrase reconnue' : pred.original_word;
            html += `
                <div style="padding: 10px; background: rgba(76, 175, 80, 0.1); border-left: 3px solid #4CAF50; border-radius: 5px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${displayTitle}</strong> → 
                            <span style="color: #4CAF50; font-weight: bold;">${pred.asl_word}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="background: rgba(76, 175, 80, 0.2); padding: 3px 8px; border-radius: 12px; font-size: 0.85rem;">
                                ✓ ${(pred.confidence * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div style="padding: 10px; background: rgba(255, 152, 0, 0.1); border-left: 3px solid #FF9800; border-radius: 5px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${pred.original_word}</strong>
                            <span style="color: #FF9800; font-size: 0.9rem; margin-left: 10px;">
                                ⚠️ Mot inconnu - Épeler lettre par lettre
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }
    });

    html += '</div>';
    existingSection.innerHTML = html;

    // Trigger 3D avatar animation for signs
    // Note: Already triggered in translateAudio, but keeping here for single display updates if needed
}

/**
 * Update sign display during animation
 */
/**
 * Update sign display during animation (Managed by avatar_3d.js)
 */
function updateSignDisplay(sign) {
    const signChar = document.getElementById('currentSignChar');
    const signName = document.getElementById('currentSignName');
    const progress = document.getElementById('animationProgress');

    if (!signChar || !signName || !progress) return;

    signChar.textContent = sign;
    signName.textContent = `Signe ASL: ${sign}`;
}

/**
 * Reset avatar to initial position
 */
function resetAvatar() {
    if (typeof initAvatarScene === 'function') {
        // Remove existing canvas
        const container = document.getElementById('avatar3DContainer');
        if (container) {
            container.innerHTML = '';
            // Reinitialize
            initAvatarScene();
        }

        // Reset display with null checks
        const signChar = document.getElementById('currentSignChar');
        const signName = document.getElementById('currentSignName');
        const progress = document.getElementById('animationProgress');

        if (signChar) signChar.textContent = '-';
        if (signName) signName.textContent = 'Prêt...';
        if (progress) progress.style.width = '0%';

        console.log('✅ Avatar reset');
    }
}

// ===== GESTION DE L'ANIMATION AVATAR PRO =====
let animationTimeouts = [];
let videoQueue = [];
let isPlayingSequence = false;

function animateSigns(signs) {
    stopAnimation(); // Stop any current animation

    // UI Elements
    const statusText = document.getElementById('avatarStatusText');
    const statusDot = document.querySelector('.status-dot');

    if (statusText) statusText.textContent = "Préparation de la séquence...";
    if (statusDot) statusDot.style.background = "#FFC107"; // Yellow for processing

    // Prepare queue - Filter out nulls or invalid entries if any
    videoQueue = signs.map(s => typeof s === 'string' ? s : (s.asl_word || s)).filter(s => s && !s.startsWith('UNKNOWN_'));

    if (videoQueue.length > 0) {
        playNextVideo(0);
    } else {
        resetAvatar();
        if (statusText) statusText.textContent = "Aucun signe connu trouvé.";
    }
}

function playNextVideo(index) {
    const avatarImg = document.getElementById('proAvatarImg');
    const videoPlayer = document.getElementById('signVideoPlayer');
    const statusText = document.getElementById('avatarStatusText');
    const progressBar = document.getElementById('animationProgress');
    const currentSignChar = document.getElementById('currentSignChar');
    const currentSignName = document.getElementById('currentSignName');

    if (index >= videoQueue.length) {
        // End of sequence
        resetAvatar();
        if (statusText) statusText.textContent = "Traduction terminée";
        if (progressBar) progressBar.style.width = '100%';
        if (currentSignName) currentSignName.textContent = 'Séquence terminée';
        return;
    }

    const word = videoQueue[index];
    isPlayingSequence = true;

    // UI Updates
    if (progressBar) {
        const percent = ((index) / videoQueue.length) * 100;
        progressBar.style.width = `${percent}%`;
    }

    // Show current word info
    if (currentSignChar) currentSignChar.textContent = word.charAt(0).toUpperCase();
    if (currentSignName) currentSignName.textContent = `Signe: ${word.toUpperCase()}`;

    // Show badge overlay as subtitle
    showSignBadge(word);

    // Try to play 3D Animation FIRST
    const has3DAnim = typeof playASLAnimation === 'function' && window.isAvatarReady;

    // Check if we have data for this sign (Checking internal dictionary of avatar_3d.js)
    // We can try calling it, if it returns true (or promise), good.
    // For now, we will prefer 3D for KNOWN words, and Video for others?
    // User SAID: "Avatar with hands". So we should TRY to use avatar for everything even if imperfect?
    // But we only have 8 procedural signs.

    // STRATEGY: 
    // If it's one of our hardcoded procedural signs -> 3D Avatar
    // Else -> Video (User might accept video if avatar is impossible, OR we show generic gesture)

    const known3DSigns = ['HELLO', 'GOOD_MORNING', 'THANKS', 'PLEASE', 'YES', 'NO', 'I', 'YOU', '21'];

    if (known3DSigns.includes(word.toUpperCase())) {
        if (avatarImg) avatarImg.style.display = 'none';
        if (videoPlayer) videoPlayer.style.display = 'none';
        const avatar3DContainer = document.getElementById('avatar3DContainer');
        if (avatar3DContainer) avatar3DContainer.style.display = 'block';

        playASLAnimation(word).then(() => {
            setTimeout(() => {
                playNextVideo(index + 1);
            }, 500);
        });
        return; // Skip video logic
    }

    // Default to Video for unknown words (better than nothing)
    // OR we could generic gesture?
    // Let's stick to video for unknown words for now, as "generic waving" is not translation.

    const videoUrl = `/api/video/${encodeURIComponent(word)}`;

    // Switch to video mode
    if (avatarImg) avatarImg.style.display = 'none';
    const avatar3DContainer = document.getElementById('avatar3DContainer');
    if (avatar3DContainer) avatar3DContainer.style.display = 'none';

    if (videoPlayer) {
        videoPlayer.classList.add('active');
        videoPlayer.style.display = 'block';
        videoPlayer.src = videoUrl;
        videoPlayer.load();

        // Handle video events
        const onCanPlay = () => {
            videoPlayer.play().catch(e => {
                console.error("Autoplay failed:", e);
                // Fallback if play fails (skip to next)
                handleVideoError(index, word);
            });
        };

        const onEnded = () => {
            // Clean up listeners
            videoPlayer.removeEventListener('canplay', onCanPlay);
            videoPlayer.removeEventListener('ended', onEnded);
            videoPlayer.removeEventListener('error', onError);

            // Play next after short pause
            setTimeout(() => {
                playNextVideo(index + 1);
            }, 500);
        };

        const onError = () => {
            videoPlayer.removeEventListener('canplay', onCanPlay);
            videoPlayer.removeEventListener('ended', onEnded);
            videoPlayer.removeEventListener('error', onError);
            handleVideoError(index, word);
        };

        videoPlayer.addEventListener('canplay', onCanPlay, { once: true });
        videoPlayer.addEventListener('ended', onEnded, { once: true });
        videoPlayer.addEventListener('error', onError, { once: true });
    } else {
        // No video player? Fallback directly
        handleVideoError(index, word);
    }
}

function handleVideoError(index, word) {
    console.warn(`Video not found or error for word: ${word}. Skipping video.`);

    const avatarImg = document.getElementById('proAvatarImg');
    const videoPlayer = document.getElementById('signVideoPlayer');

    // Hide video, show image container
    if (videoPlayer) {
        videoPlayer.classList.remove('active');
        videoPlayer.style.display = 'none'; // Ensure hidden
        videoPlayer.pause();
    }
    if (avatarImg) {
        avatarImg.style.display = 'block'; // Force display block
        // Reset to default image or keep current
        avatarImg.src = "/static/images/avatar_pro.png";
    }

    // Show badge for duration even if video missing
    showSignBadge(word + " (Vidéo manquante)");

    // Wait standard duration before next
    setTimeout(() => {
        playNextVideo(index + 1);
    }, 1500);
}

// playFingerspelling removed as per user request

function showSignBadge(sign) {
    const container = document.getElementById('signBadgeContainer');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Create Badge
    const badge = document.createElement('div');
    badge.className = 'sign-badge';
    badge.textContent = sign; // Show the sign text

    container.appendChild(badge);

    // Update Info Display
    const currentSignChar = document.getElementById('currentSignChar');
    const currentSignName = document.getElementById('currentSignName');

    if (currentSignChar) currentSignChar.textContent = sign.charAt(0);
    if (currentSignName) currentSignName.textContent = `Signe: ${sign}`;
}

function showSignBadge(sign) {
    const container = document.getElementById('signBadgeContainer');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Create Badge
    const badge = document.createElement('div');
    badge.className = 'sign-badge';
    badge.textContent = sign; // Show the sign text

    container.appendChild(badge);

    // Update Info Display
    const currentSignChar = document.getElementById('currentSignChar');
    const currentSignName = document.getElementById('currentSignName');

    if (currentSignChar) currentSignChar.textContent = sign.charAt(0);
    if (currentSignName) currentSignName.textContent = `Signe: ${sign}`;
}

function stopAnimation() {
    isPlayingSequence = false;
    animationTimeouts.forEach(id => clearTimeout(id));
    animationTimeouts = [];

    const videoPlayer = document.getElementById('signVideoPlayer');
    if (videoPlayer) {
        videoPlayer.pause();
        videoPlayer.classList.remove('active');
        videoPlayer.src = "";
        // Remove listeners by cloning (simplest reset) or assumed handled by {once:true}
    }

    const avatarImg = document.getElementById('proAvatarImg');
    if (avatarImg) {
        avatarImg.classList.remove('hidden');
        avatarImg.src = "/static/images/avatar_pro.png"; // Reset to default
    }

    const container = document.getElementById('signBadgeContainer');
    if (container) container.innerHTML = '';
}

function resetAvatar() {
    stopAnimation();
    const statusText = document.getElementById('avatarStatusText');
    const progressBar = document.getElementById('animationProgress');
    const signChar = document.getElementById('currentSignChar');
    const signName = document.getElementById('currentSignName');
    const statusDot = document.querySelector('.status-dot');

    // UI Reset
    const avatarImg = document.getElementById('proAvatarImg');
    const avatar3DContainer = document.getElementById('avatar3DContainer');
    const videoPlayer = document.getElementById('signVideoPlayer');

    if (videoPlayer) {
        videoPlayer.classList.remove('active');
        videoPlayer.style.display = 'none';
    }

    if (avatar3DContainer) {
        avatar3DContainer.style.display = 'block';
    } else if (avatarImg) {
        // Fallback if 3D not present
        avatarImg.style.display = 'block';
        avatarImg.src = "/static/images/avatar_pro.png";
    }

    if (statusText) statusText.textContent = "Prêt à signer";
    if (statusDot) statusDot.style.background = "#4CAF50"; // Green
    if (progressBar) progressBar.style.width = '0%';
    if (signChar) signChar.textContent = '✓';
    if (signName) signName.textContent = 'Système Prêt';
}

// ===== GESTION DE L'HISTORIQUE =====
function saveToHistory(text) {
    let history = JSON.parse(localStorage.getItem('asl_translation_history') || '[]');
    const newEntry = {
        text: text,
        timestamp: new Date().toISOString()
    };

    // Ajouter au début et garder les 5 derniers
    history.unshift(newEntry);
    history = history.slice(0, 5);

    localStorage.setItem('asl_translation_history', JSON.stringify(history));
    renderHistory();
}

function renderHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    const history = JSON.parse(localStorage.getItem('asl_translation_history') || '[]');

    if (history.length === 0) {
        historyList.innerHTML = '<p class="placeholder">Aucun historique pour le moment.</p>';
        return;
    }

    historyList.innerHTML = history.map(item => `
        <div class="history-item" onclick="replayHistory('${item.text.replace(/'/g, "\\'")}')">
            <div class="history-text">${item.text}</div>
            <div class="history-time">${new Date(item.timestamp).toLocaleTimeString()}</div>
        </div>
    `).join('');
}

async function replayHistory(text) {
    const transcribedText = document.getElementById('transcribedText');
    transcribedText.innerHTML = `<p style="font-size: 1.2rem; line-height: 1.8;">${text}</p>`;

    try {
        const response = await fetch('/api/text_to_signs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const result = await response.json();
        if (response.ok && result.signs) {
            animateSigns(result.signs);
        }
    } catch (e) {
        console.error('Error replaying history:', e);
    }
}

// Charger l'historique au démarrage
document.addEventListener('DOMContentLoaded', renderHistory);

// ===== FONCTIONS D'ENTRAÎNEMENT (TRAINING) =====
function openTrainingModal() {
    const text = document.getElementById('saveTrainingBtn').getAttribute('data-text');
    document.getElementById('trainingWord').value = text;
    document.getElementById('trainingModal').style.display = 'flex';
}

function closeTrainingModal() {
    document.getElementById('trainingModal').style.display = 'none';
}

async function submitTrainingData() {
    const word = document.getElementById('trainingWord').value;
    if (!currentAudioBlob) return;

    const confirmBtn = document.getElementById('confirmTrainingBtn');
    const originalText = confirmBtn.textContent;
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Envoi...';

    const formData = new FormData();
    formData.append('audio', currentAudioBlob);
    formData.append('word', word);

    try {
        const response = await fetch('/api/training/save', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            alert('Échantillon sauvegardé avec succès dans le dataset d\'entraînement !');
            closeTrainingModal();
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    } catch (e) {
        console.error('Error saving training data:', e);
        alert('Erreur réseau lors de la sauvegarde.');
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = originalText;
    }
}

