# Application de Reconnaissance de Langue des Signes Américaine (ASL)

Application Flask complète pour la reconnaissance et l'apprentissage de la langue des signes américaine utilisant un modèle CNN entraîné.

## 🎯 Fonctionnalités

### 1. **Prédiction d'Image**
- Upload d'images de signes ASL
- Prédiction avec confiance
- Affichage de toutes les prédictions possibles

### 2. **Prédiction En Ligne (Webcam)**
- Utilisation de la webcam pour la reconnaissance en temps réel
- Prédiction automatique toutes les 500ms
- Historique des prédictions capturées

### 3. **Traduction Audio**
- Enregistrement audio ou upload de fichier
- Transcription de l'audio en texte
- Conversion du texte en séquence de signes ASL
- Animation 3D d'une cartouche traduisant les signes

### 4. **Quiz Interactif**
- Quiz avec les images du dossier `images/`
- Questions aléatoires
- Affichage du score et des résultats

### 5. **Page Éducative**
- Affichage de toutes les images avec leurs significations
- Recherche et filtrage des signes
- Détails pour chaque signe avec conseils

## 📋 Prérequis

- Python 3.8 ou supérieur
- TensorFlow 2.15.0
- Toutes les dépendances listées dans `requirements.txt`

## 🚀 Installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

3. **Vérifier que le modèle est présent**:
   - Le fichier `milleur_model_nadam.h5` doit être dans le répertoire racine
   - Le dossier `images/` doit contenir les 29 images de signes ASL

4. **Structure des fichiers**:
```
.
├── app.py                      # Application Flask principale
├── milleur_model_nadam.h5      # Modèle CNN entraîné
├── requirements.txt            # Dépendances Python
├── images/                     # Images des signes ASL
│   ├── asl_a.jpg
│   ├── asl_b.jpg
│   ├── ...
│   ├── asl_z.jpg
│   ├── asl_del.jpg
│   ├── asl_nothing.jpg
│   └── asl_space.jpg
├── templates/                  # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── predict.html
│   ├── predict_online.html
│   ├── audio_translate.html
│   ├── quiz.html
│   └── education.html
├── static/                     # Fichiers statiques
│   ├── css/
│   │   ├── style.css
│   │   └── audio_translate.css
│   └── js/
│       ├── main.js
│       ├── predict.js
│       ├── predict_online.js
│       ├── audio_translate.js
│       ├── quiz.js
│       └── education.js
└── uploads/                    # Dossier pour les uploads (créé automatiquement)
```

## 🏃 Exécution

1. **Démarrer l'application Flask**:
```bash
python app.py
```

2. **Ouvrir le navigateur**:
   - Accéder à `http://localhost:5000`
   - L'application sera disponible sur toutes les interfaces réseau

## 📝 Classes ASL (29 classes)

Le modèle reconnaît 29 classes :
- **26 lettres**: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
- **3 signes spéciaux**: del, nothing, space

## 🎨 Interface Utilisateur

- **Design moderne et responsive**
- **Palette de couleurs**: Bleu (#004E89) et Orange (#FF6B35)
- **Animations légères** pour une meilleure expérience utilisateur
- **Compatible mobile, tablette et desktop**

## 🔧 Configuration

### Modifier la taille d'image du modèle

Si votre modèle utilise une taille d'image différente de 64x64, modifiez la fonction `preprocess_image` dans `app.py`:

```python
def preprocess_image(image):
    # Changer (64, 64) par la taille de votre modèle
    img = img.resize((64, 64))
    # ...
```

### Modifier la langue de reconnaissance vocale

Dans `app.py`, fonction `api_audio_to_text`, modifiez le paramètre `language`:

```python
text = r.recognize_google(audio, language='fr-FR')  # ou 'en-US'
```

## 📱 Utilisation

### Prédiction d'Image
1. Aller sur la page "Prédiction Image"
2. Uploader une image de signe ASL
3. Cliquer sur "Prédire"
4. Voir les résultats avec confiance

### Prédiction En Ligne
1. Aller sur la page "Prédiction En Ligne"
2. Cliquer sur "Démarrer la Webcam"
3. Autoriser l'accès à la caméra
4. Faire un signe devant la caméra
5. La prédiction se fait automatiquement

### Traduction Audio
1. Aller sur la page "Traduction Audio"
2. Enregistrer un audio ou uploader un fichier
3. Cliquer sur "Traduire en ASL"
4. Voir l'animation 3D des signes

### Quiz
1. Aller sur la page "Quiz"
2. Répondre aux questions
3. Voir votre score à la fin

### Éducation
1. Aller sur la page "Éducation"
2. Parcourir tous les signes
3. Cliquer sur "Détails" pour plus d'informations

## ⚠️ Notes Importantes

1. **Reconnaissance vocale**: Nécessite une connexion internet pour utiliser l'API Google Speech Recognition
2. **Webcam**: Nécessite l'autorisation d'accès à la caméra dans le navigateur
3. **Microphone**: Nécessite l'autorisation d'accès au microphone pour l'enregistrement audio
4. **Modèle**: Assurez-vous que le modèle `milleur_model_nadam.h5` est compatible avec TensorFlow 2.15.0

## 🐛 Dépannage

### Erreur de chargement du modèle
- Vérifiez que le fichier `milleur_model_nadam.h5` existe
- Vérifiez que TensorFlow est correctement installé
- Vérifiez les logs pour plus de détails

### Erreur de reconnaissance vocale
- Vérifiez votre connexion internet
- Vérifiez que le format audio est supporté (WAV recommandé)
- Essayez de parler plus clairement

### Erreur de webcam
- Vérifiez que la caméra est connectée
- Autorisez l'accès à la caméra dans les paramètres du navigateur
- Essayez un autre navigateur (Chrome recommandé)

## 📄 Licence

Ce projet est libre d'utilisation pour des projets éducatifs et personnels.

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.

---

**Créé avec ❤️ pour l'apprentissage de la langue des signes américaine**

