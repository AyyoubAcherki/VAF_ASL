// ===== PREDICT IMAGE PAGE =====
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const previewArea = document.getElementById('previewArea');
const previewImage = document.getElementById('previewImage');
const predictBtn = document.getElementById('predictBtn');
const resultArea = document.getElementById('resultArea');
const loading = document.getElementById('loading');

let selectedFile = null;

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#FF6B35';
    uploadArea.style.background = '#FFF4F0';
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#004E89';
    uploadArea.style.background = '#E8F4F8';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#004E89';
    uploadArea.style.background = '#E8F4F8';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input change
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        alert('Veuillez sélectionner une image valide');
        return;
    }
    
    selectedFile = file;
    
    // Afficher la prévisualisation
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        previewArea.style.display = 'block';
        resultArea.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    selectedFile = null;
    previewImage.src = '';
    uploadArea.style.display = 'block';
    previewArea.style.display = 'none';
    resultArea.style.display = 'none';
    imageInput.value = '';
}

async function predictImage() {
    if (!selectedFile) {
        alert('Veuillez sélectionner une image');
        return;
    }
    
    // Afficher le loading
    loading.style.display = 'block';
    resultArea.style.display = 'none';
    predictBtn.disabled = true;
    
    // Préparer le formulaire
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayResult(result);
        } else {
            alert('Erreur: ' + (result.error || 'Erreur lors de la prédiction'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors de la prédiction: ' + error.message);
    } finally {
        loading.style.display = 'none';
        predictBtn.disabled = false;
    }
}

function displayResult(result) {
    // Afficher la prédiction principale
    document.getElementById('predictedClass').textContent = result.class;
    document.getElementById('confidenceValue').textContent = (result.confidence * 100).toFixed(2) + '%';
    
    // Afficher la barre de confiance
    const confidenceFill = document.getElementById('confidenceFill');
    confidenceFill.style.width = (result.confidence * 100) + '%';
    
    // Afficher toutes les prédictions
    const predictionsList = document.getElementById('predictionsList');
    predictionsList.innerHTML = '';
    
    if (result.all_predictions) {
        // Trier par confiance
        const sortedPredictions = Object.entries(result.all_predictions)
            .sort((a, b) => b[1] - a[1]);
        
        sortedPredictions.forEach(([className, confidence]) => {
            const item = document.createElement('div');
            item.className = 'prediction-item';
            item.innerHTML = `
                <div style="font-weight: 600; color: ${confidence > 0.1 ? '#004E89' : '#999'}">${className}</div>
                <div style="font-size: 0.75rem; color: #666">${(confidence * 100).toFixed(1)}%</div>
            `;
            predictionsList.appendChild(item);
        });
    }
    
    // Afficher la zone de résultat
    resultArea.style.display = 'block';
    resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

