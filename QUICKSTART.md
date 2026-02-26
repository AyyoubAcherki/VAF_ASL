# Guide de Démarrage Rapide

## Installation Rapide

1. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

2. **Vérifier les fichiers**:
   - ✅ `milleur_model_nadam.h5` existe
   - ✅ Dossier `images/` contient 29 images ASL
   - ✅ Tous les fichiers templates et static sont présents

3. **Démarrer l'application**:
```bash
python app.py
```

Ou utilisez les scripts:
- Windows: `run.bat`
- Linux/Mac: `chmod +x run.sh && ./run.sh`

4. **Ouvrir le navigateur**:
   - Aller sur: http://localhost:5000

## Utilisation

### Prédiction d'Image
1. Cliquez sur "Prédiction Image"
2. Upload une image de signe ASL
3. Cliquez sur "Prédire"
4. Voir les résultats

### Prédiction En Ligne
1. Cliquez sur "Prédiction En Ligne"
2. Autorisez l'accès à la caméra
3. Faites un signe devant la caméra
4. La prédiction se fait automatiquement

### Traduction Audio
1. Cliquez sur "Traduction Audio"
2. Enregistrez ou uploadez un fichier audio
3. Cliquez sur "Traduire en ASL"
4. Regardez l'animation 3D

### Quiz
1. Cliquez sur "Quiz"
2. Répondez aux questions
3. Voyez votre score

### Éducation
1. Cliquez sur "Éducation"
2. Parcourez tous les signes
3. Cliquez sur "Détails" pour plus d'infos

## Dépannage

### Le modèle ne se charge pas
- Vérifiez que `milleur_model_nadam.h5` existe
- Vérifiez que TensorFlow est installé: `pip install tensorflow`

### Erreur de webcam
- Autorisez l'accès à la caméra dans le navigateur
- Utilisez Chrome ou Firefox
- Vérifiez que la caméra fonctionne

### Erreur de reconnaissance vocale
- Vérifiez votre connexion internet
- Utilisez un fichier audio en format WAV
- Parlez clairement

### Les images ne s'affichent pas
- Vérifiez que le dossier `images/` contient les 29 images
- Vérifiez les noms des fichiers (asl_a.jpg, asl_b.jpg, etc.)

## Support

Pour plus d'informations, consultez `README_ASL.md`

