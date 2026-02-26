// ===== EDUCATION PAGE =====
function filterSigns(type) {
    const signCards = document.querySelectorAll('.sign-card');
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    // Mettre à jour les boutons actifs
    filterButtons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Filtrer les cartes
    signCards.forEach(card => {
        if (type === 'all') {
            card.style.display = 'block';
        } else {
            const cardType = card.getAttribute('data-type');
            if (cardType === type) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        }
    });
}

// Recherche
document.getElementById('searchInput').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const signCards = document.querySelectorAll('.sign-card');
    
    signCards.forEach(card => {
        const signName = card.getAttribute('data-name').toLowerCase();
        if (signName.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});

function showSignDetails(class_name, meaning, imageUrl) {
    const modal = document.getElementById('signModal');
    const modalClass = document.getElementById('modalClass');
    const modalMeaning = document.getElementById('modalMeaning');
    const modalImage = document.getElementById('modalImage');
    const modalTips = document.getElementById('modalTips');
    
    modalClass.textContent = class_name;
    modalMeaning.textContent = meaning;
    modalImage.src = imageUrl;
    
    // Générer des conseils selon le type de signe
    const tips = generateTips(class_name);
    modalTips.innerHTML = '';
    tips.forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        modalTips.appendChild(li);
    });
    
    modal.style.display = 'flex';
}

function closeSignModal() {
    document.getElementById('signModal').style.display = 'none';
}

function generateTips(class_name) {
    const tipsMap = {
        'A': [
            'Formez un poing avec votre main',
            'Le pouce doit être plié sur le côté',
            'Tenez votre main devant vous, paume face à vous'
        ],
        'B': [
            'Gardez tous les doigts droits et ensemble',
            'Le pouce doit être replié contre la paume',
            'Tenez votre main verticalement'
        ],
        'SPACE': [
            'Écartez les doigts de votre main',
            'Déplacez votre main d\'un côté à l\'autre',
            'Utilisez ce signe pour représenter un espace entre les mots'
        ],
        'DEL': [
            'Formez un poing',
            'Faites un mouvement de suppression',
            'Utilisez ce signe pour indiquer une suppression'
        ],
        'NOTHING': [
            'Gardez votre main ouverte',
            'Faites un mouvement de balayement',
            'Utilisez ce signe pour indiquer "rien"'
        ]
    };
    
    // Conseils génériques pour les lettres
    if (tipsMap[class_name]) {
        return tipsMap[class_name];
    } else {
        return [
            'Pratiquez le signe régulièrement',
            'Assurez-vous que votre main est bien visible',
            'Maintenez une position confortable',
            'Observez des locuteurs natifs pour apprendre la bonne forme'
        ];
    }
}

// Fermer la modal en cliquant en dehors
window.addEventListener('click', (e) => {
    const modal = document.getElementById('signModal');
    if (e.target === modal) {
        closeSignModal();
    }
});

// Fermer la modal avec la touche Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeSignModal();
    }
});

