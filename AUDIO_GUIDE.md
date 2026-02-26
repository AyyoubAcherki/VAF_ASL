# Guide de Reconnaissance Audio ASL

## Améliorations Apportées

Le système de reconnaissance audio a été amélioré avec :

### 1. **Paramètres Optimisés**

- **Energy Threshold**: Réduit à 300 pour capter plus de sons
- **Dynamic Energy Threshold**: Activé pour s'adapter automatiquement
- **Pause Threshold**: 0.8 secondes pour une meilleure détection de fin de parole

### 2. **Reconnaissance Multi-Langue**

Le système essaie maintenant 3 langues dans l'ordre :

1. **Français** (fr-FR)
2. **Anglais** (en-US)
3. **Arabe** (ar-MA)

### 3. **Messages d'Erreur Détaillés**

En cas d'échec, vous recevrez :

- Les détails de chaque tentative
- Des suggestions concrètes pour améliorer la reconnaissance

## Conseils pour une Meilleure Reconnaissance

### ✅ Bonnes Pratiques

1. **Qualité Audio**
   - Utilisez un microphone de bonne qualité
   - Enregistrez dans un environnement calme
   - Évitez le bruit de fond (ventilateur, musique, etc.)

2. **Enregistrement**
   - Parlez clairement et distinctement
   - Maintenez une distance constante du microphone (15-30 cm)
   - Parlez à un volume normal (ni trop fort, ni trop bas)
   - Enregistrez au moins 1-2 secondes de parole

3. **Format Audio**
   - **Recommandé**: WAV (pas de conversion nécessaire)
   - **Supportés**: MP3, OGG, WebM, M4A, FLAC (nécessite FFmpeg)
   - **Qualité**: 16kHz, 16-bit, mono

### ❌ À Éviter

- Audio trop court (moins de 0.5 secondes)
- Bruit de fond excessif
- Volume trop faible
- Parler trop vite
- Microphone de mauvaise qualité
- Connexion internet instable

## Formats Audio Supportés

| Format | Extension | Nécessite FFmpeg | Notes |
|--------|-----------|------------------|-------|
| WAV | `.wav` | ❌ Non | Format recommandé |
| MP3 | `.mp3` | ✅ Oui | Très courant |
| OGG | `.ogg` | ✅ Oui | Open source |
| WebM | `.webm` | ✅ Oui | Format web |
| M4A | `.m4a` | ✅ Oui | Apple |
| FLAC | `.flac` | ✅ Oui | Sans perte |

## Installation de FFmpeg

Si vous utilisez des formats autres que WAV, installez FFmpeg :

### Windows

```powershell
# Télécharger depuis https://ffmpeg.org/download.html
# Extraire dans C:\ffmpeg
# Ajouter C:\ffmpeg\bin au PATH
```

Voir [INSTALL_FFMPEG.md](INSTALL_FFMPEG.md) pour plus de détails.

## Dépannage

### Erreur: "Impossible de reconnaître l'audio"

**Solutions possibles:**

1. **Vérifier la qualité audio**

   ```
   - Ouvrez le fichier dans un lecteur audio
   - Vérifiez que vous entendez clairement la parole
   - Assurez-vous qu'il n'y a pas que du silence
   ```

2. **Augmenter le volume**
   - Parlez plus fort lors de l'enregistrement
   - Rapprochez-vous du microphone

3. **Réduire le bruit**
   - Fermez les fenêtres
   - Éteignez les ventilateurs/climatisation
   - Enregistrez dans une pièce calme

4. **Tester avec différentes langues**
   - Le système teste automatiquement FR, EN, AR
   - Vérifiez les détails de l'erreur pour voir quelle langue a été testée

5. **Vérifier la connexion internet**
   - La reconnaissance utilise Google Speech API
   - Une connexion stable est nécessaire

### Erreur: "Format audio non supporté"

**Solutions:**

- Convertissez en WAV
- Installez FFmpeg pour supporter d'autres formats

### Erreur: "Le fichier audio est vide"

**Solutions:**

- Vérifiez que l'enregistrement a bien fonctionné
- Assurez-vous que le fichier n'est pas corrompu
- Enregistrez un audio plus long (minimum 1 seconde)

## Exemple d'Utilisation

### Via l'Interface Web

1. Allez sur la page "Traduction Audio"
2. Cliquez sur le bouton d'enregistrement
3. Parlez clairement pendant 2-3 secondes
4. Arrêtez l'enregistrement
5. Le texte transcrit apparaîtra automatiquement
6. Les signes ASL correspondants seront affichés

### Via l'API

```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'recording.wav');

fetch('/api/audio_to_text', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.text) {
        console.log('Texte reconnu:', data.text);
    } else if (data.error) {
        console.error('Erreur:', data.error);
        console.log('Suggestions:', data.suggestions);
    }
});
```

## Support

Si vous continuez à rencontrer des problèmes :

1. Vérifiez les logs du serveur pour plus de détails
2. Testez avec un fichier WAV simple
3. Vérifiez votre connexion internet
4. Assurez-vous que Google Speech API est accessible depuis votre région
