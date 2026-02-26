# Installation de FFmpeg pour la Conversion Audio

Pour que l'application puisse convertir les formats audio (MP3, WebM, OGG, etc.) en WAV, vous devez installer FFmpeg.

## Windows

### Option 1: Téléchargement Direct
1. Téléchargez FFmpeg depuis: https://www.gyan.dev/ffmpeg/builds/
2. Téléchargez la version "ffmpeg-release-essentials.zip"
3. Extrayez l'archive dans un dossier (par exemple: `C:\ffmpeg`)
4. Ajoutez `C:\ffmpeg\bin` à votre PATH système:
   - Ouvrez "Variables d'environnement" (Win + R, tapez `sysdm.cpl`, onglet "Avancé")
   - Cliquez sur "Variables d'environnement"
   - Dans "Variables système", trouvez "Path" et cliquez sur "Modifier"
   - Cliquez sur "Nouveau" et ajoutez: `C:\ffmpeg\bin`
   - Cliquez sur "OK" pour fermer toutes les fenêtres
   - Redémarrez votre terminal ou votre IDE

### Chemin Spécifique
Si FFmpeg est installé dans `C:\ffmpeg\bin`, assurez-vous que ce chemin est dans votre PATH. Vous pouvez vérifier avec:
```bash
echo %PATH%
```

Pour tester si FFmpeg est accessible:
```bash
C:\ffmpeg\bin\ffmpeg.exe -version
```

### Option 2: Avec Chocolatey
```bash
choco install ffmpeg
```

### Option 3: Avec Scoop
```bash
scoop install ffmpeg
```

## Linux

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### CentOS/RHEL
```bash
sudo yum install ffmpeg
```

## macOS

### Avec Homebrew
```bash
brew install ffmpeg
```

## Vérification de l'Installation

Après l'installation, vérifiez que FFmpeg est installé:

```bash
ffmpeg -version
```

Vous devriez voir la version de FFmpeg affichée.

## Alternative: Utiliser uniquement WAV

Si vous ne pouvez pas installer FFmpeg, vous pouvez:
1. Utiliser uniquement des fichiers WAV pour l'upload
2. L'enregistrement depuis le navigateur fonctionnera toujours (le format WebM sera géré si possible)

## Note

- FFmpeg est nécessaire pour convertir MP3, WebM, OGG, M4A, FLAC en WAV
- Les fichiers WAV fonctionnent sans FFmpeg
- L'application détectera automatiquement si FFmpeg est disponible

