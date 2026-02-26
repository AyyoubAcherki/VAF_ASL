# Complete Audio-to-ASL Translation with 3D Avatar

## 🎯 System Overview

This is a complete working prototype that combines:

- **Audio Input** → Speech-to-Text (Google API)
- **Text Processing** → ASL Word Prediction (CNN-LSTM model)
- **3D Avatar Animation** → Real-time ASL sign visualization (Three.js)

## 📁 File Structure

```
backend/
├── server/
│   └── routes.py                    # Flask API endpoint
├── utils/
│   └── predict_video.py             # Text-to-ASL mapping logic
├── templates/
│   └── audio_translate.html         # Main UI page
├── static/
│   └── js/
│       ├── audio_translate.js       # Frontend logic
│       └── avatar_3d.js             # Three.js 3D avatar system
└── model/
    └── cnn_lstm_words_aug_best.h5   # CNN-LSTM model
```

## 🔧 Backend Implementation

### 1. API Endpoint (`routes.py`)

**Endpoint**: `POST /api/audio/translate/asl`

**Features**:

- Multi-format audio support (WAV, MP3, OGG, WebM, M4A, FLAC)
- Multi-language speech recognition (FR/EN/AR)
- ASL word prediction with confidence scores
- Graceful error handling

**Response Format**:

```json
{
  "text": "bonjour merci",
  "detected_language": "fr",
  "asl_predictions": [
    {
      "original_word": "bonjour",
      "asl_word": "HELLO",
      "confidence": 1.0,
      "status": "found"
    },
    {
      "original_word": "merci",
      "asl_word": "THANKS",
      "confidence": 1.0,
      "status": "found"
    }
  ],
  "total_words": 2,
  "found_words": 2,
  "unknown_words": 0
}
```

### 2. ASL Prediction Logic (`predict_video.py`)

**Key Functions**:

- `preprocess_word(word)`: Normalizes and translates words
- `predict_text_to_asl(text)`: Maps text to ASL signs
- `get_asl_vocabulary()`: Returns supported vocabulary

**Vocabulary**: 120+ ASL words including:

- Greetings: hello, hi, goodbye, thanks, please
- Actions: help, stop, go, eat, drink, sleep
- Qualifiers: good, bad, happy, sad, big, small
- Questions: what, where, when, who, why, how

**Language Support**:

- French → English translation
- Arabic → English translation
- Direct English support

## 🎨 Frontend Implementation

### 3. HTML Template (`audio_translate.html`)

**Components**:

- Audio input (record/upload)
- Translation button
- Text display with language detection
- ASL predictions with confidence scores
- 3D avatar container (500px height)
- Progress indicators

**Libraries**:

- Three.js r128 (3D graphics)
- Custom avatar animation system

### 4. Avatar Animation System (`avatar_3d.js`)

**Features**:

- **Scene Setup**: Camera, lights, renderer
- **Simple Avatar**: Procedural humanoid (head, body, arms, hands, legs)
- **Animation System**: Keyframe-based procedural animations
- **ASL Signs**: HELLO, THANKS, PLEASE, YES, NO (expandable)

**Key Functions**:

```javascript
initAvatarScene()              // Initialize Three.js scene
createSimpleAvatar()           // Create humanoid avatar
playASLAnimation(sign)         // Animate single ASL sign
playASLSequence(signs)         // Animate sequence of signs
getASLAnimationData(sign)      // Get animation keyframes
```

**Animation Structure**:

```javascript
{
  name: 'hello',
  duration: 1.5,
  keyframes: [
    { time: 0, rightHand: { y: 1.4, z: 0.2 }, rightArm: { rotation: { z: -0.5 } } },
    { time: 0.5, rightHand: { y: 1.6, z: 0.3 }, rightArm: { rotation: { z: -0.3 } } },
    { time: 1.5, rightHand: { y: 0.95, z: 0 }, rightArm: { rotation: { z: -Math.PI/6 } } }
  ]
}
```

## 🚀 Usage Flow

### End-to-End Process

1. **User Records/Uploads Audio**

   ```
   User clicks "Enregistrer" or uploads audio file
   ```

2. **Frontend Sends to API**

   ```javascript
   POST /api/audio/translate/asl
   FormData: { audio: audioBlob }
   ```

3. **Backend Processing**

   ```
   Audio → WAV conversion (if needed)
   → Speech Recognition (FR/EN/AR)
   → Text tokenization
   → ASL word mapping
   → Response with predictions
   ```

4. **Frontend Displays Results**

   ```
   - Recognized text with language emoji
   - Statistics (total/found/unknown words)
   - Word-by-word ASL predictions
   - Confidence scores
   ```

5. **3D Avatar Animation**

   ```javascript
   playASLSequence(['HELLO', 'THANKS'])
   → Animates avatar performing each sign sequentially
   → Updates progress bar
   ```

## 🎭 3D Avatar Details

### Current Implementation

**Simple Humanoid Avatar**:

- Created using Three.js primitives (spheres, cylinders)
- Fully functional and animatable
- Placeholder for GLTF/FBX model

**Animation Method**:

- Procedural keyframe interpolation
- Smooth transitions between poses
- Configurable duration and timing

### Upgrading to Real GLTF Model

To use a real 3D model, update `avatar_3d.js`:

```javascript
function loadAvatar() {
    const loader = new THREE.GLTFLoader();
    loader.load(
        '/static/models/avatar.glb',  // Your model path
        (gltf) => {
            avatar = gltf.scene;
            scene.add(avatar);
            
            // Use model's built-in animations
            mixer = new THREE.AnimationMixer(avatar);
            currentAnimations = gltf.animations;
            
            isAvatarReady = true;
        }
    );
}
```

### Adding Real ASL Animations

**Option 1: Use Model Animations**

```javascript
function playASLAnimation(aslSign) {
    const animationClip = currentAnimations.find(a => a.name === aslSign);
    if (animationClip) {
        const action = mixer.clipAction(animationClip);
        action.reset().play();
    }
}
```

**Option 2: Motion Capture Data**

- Import BVH/FBX animation files
- Map to avatar skeleton
- Play via AnimationMixer

**Option 3: Expand Keyframes**
Add more detailed keyframes in `getASLAnimationData()`:

```javascript
'WATER': {
    name: 'water',
    duration: 2.0,
    keyframes: [
        // Detailed hand positions, finger poses, etc.
    ]
}
```

## 📊 Testing

### Test Scenarios

**1. French Audio**

```
Input: "Bonjour merci"
Expected: HELLO → THANKS animation
```

**2. English Audio**

```
Input: "Hello please help"
Expected: HELLO → PLEASE → HELP animation
```

**3. Unknown Words**

```
Input: "Hello ordinateur"
Expected: HELLO animation + warning for "ordinateur"
```

**4. Arabic Audio**

```
Input: "مرحبا شكرا"
Expected: HELLO → THANKS animation
```

## 🔧 Configuration

### Adding New ASL Words

**1. Update Vocabulary** (`predict_video.py`):

```python
ASL_WORDS = [
    # ... existing words ...
    'water', 'food', 'coffee'  # Add new words
]
```

**2. Add Translation** (if needed):

```python
FRENCH_TO_ENGLISH = {
    # ... existing ...
    'eau': 'water',
    'nourriture': 'food'
}
```

**3. Add Animation** (`avatar_3d.js`):

```javascript
'WATER': {
    name: 'water',
    duration: 1.5,
    keyframes: [
        // Define animation keyframes
    ]
}
```

## 🎯 Key Features

✅ **Modular Architecture**: Each component is independent  
✅ **Multi-Language Support**: FR/EN/AR speech recognition  
✅ **Real-Time Animation**: Smooth 3D avatar movements  
✅ **Confidence Scores**: Shows prediction certainty  
✅ **Error Handling**: Graceful fallbacks for unknown words  
✅ **Extensible**: Easy to add new words and animations  
✅ **Non-Intrusive**: Doesn't affect existing image prediction  

## 🚧 Future Enhancements

### Short Term

- [ ] Load professional GLTF avatar model
- [ ] Add more ASL sign animations (50+ words)
- [ ] Implement fingerspelling for unknown words
- [ ] Add camera controls (zoom, rotate)

### Medium Term

- [ ] Real motion capture ASL animations
- [ ] Facial expressions for ASL grammar
- [ ] Multiple avatar options
- [ ] Animation speed control

### Long Term

- [ ] Real-time webcam ASL recognition
- [ ] Bidirectional translation (ASL → Text)
- [ ] VR/AR support
- [ ] Mobile app integration

## 📝 Notes

- **Model Path**: Ensure `cnn_lstm_words_aug_best.h5` is in `backend/model/`
- **FFmpeg**: Required for non-WAV audio formats
- **Internet**: Required for Google Speech API
- **Browser**: Modern browser with WebGL support for 3D

## 🎬 Demo Flow

1. Open `http://localhost:5000/audio_translate`
2. Click "Enregistrer" and say "Bonjour merci"
3. Click "Traduire en ASL"
4. Watch:
   - Text appears: "🇫🇷 bonjour merci"
   - Predictions show: HELLO (✓ 100%), THANKS (✓ 100%)
   - 3D avatar performs HELLO then THANKS signs
   - Progress bar updates in real-time

---

**Status**: ✅ Fully Functional Prototype  
**Ready for**: Testing, Refinement, Real Model Integration
