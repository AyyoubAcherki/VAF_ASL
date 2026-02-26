# ASL Animation Extraction Scripts

This directory contains scripts to extract pose data from ASL training videos and convert them to avatar animations.

## 📁 Files

- **`extract_pose_from_video.py`** - Extract pose from a single video
- **`batch_process_videos.py`** - Batch process all training videos
- **`test_extraction.py`** - Test extraction on sample videos

## 🚀 Quick Start

### 1. Install Dependencies

```bash
conda install -c conda-forge mediapipe opencv
```

### 2. Test Extraction

Test on a few sample videos first:

```bash
python scripts/test_extraction.py
```

### 3. Process Single Video

Extract pose from one video:

```bash
python scripts/extract_pose_from_video.py train/21/21_801.mp4
```

This will:

- Extract hand and body poses using MediaPipe
- Calculate finger curl values
- Save JSON keyframe data to `backend/animations/keyframes/21.json`
- Print JavaScript code to add to `avatar_3d.js`

### 4. Batch Process Priority Signs

Process Phase 1 priority signs (numbers, greetings, actions, emotions):

```bash
python scripts/batch_process_videos.py --phase 1
```

### 5. Process All Signs

Process all 648 signs:

```bash
python scripts/batch_process_videos.py
```

## 📊 Output

### JSON Keyframes

Each sign gets a JSON file in `backend/animations/keyframes/`:

```json
{
  "name": "hello",
  "duration": 1.5,
  "keyframes": [
    {
      "time": 0.0,
      "rightHand": {
        "pos": { "x": 0.2, "y": 1.4, "z": 0.1 }
      },
      "fingers": {
        "right": {
          "thumb": 0.0,
          "index": 0.0,
          "middle": 0.0,
          "ring": 0.0,
          "pinky": 0.0
        }
      }
    }
  ]
}
```

### Combined JavaScript

All animations are combined into `backend/animations/asl_animations.js`:

```javascript
const ASL_ANIMATIONS = {
    'HELLO': {
        duration: 1.5,
        keyframes: [...]
    },
    'THANKS': {
        duration: 1.2,
        keyframes: [...]
    }
    // ... 648 total
};
```

## 🎯 Processing Phases

### Phase 1: Priority Signs (157 signs)

- Numbers: 21-30, zero-twenty
- Greetings: hello, thanks, goodbye, etc.
- Actions: eat, drink, sleep, help, etc.
- Emotions: happy, sad, angry, etc.

```bash
python scripts/batch_process_videos.py --phase 1
```

### Phase 2: Extended Vocabulary (200 signs)

- Colors, animals, weather, clothing, sports, etc.

### Phase 3: Remaining Signs (291 signs)

- All other signs

## 🔧 Command Options

### extract_pose_from_video.py

```bash
python scripts/extract_pose_from_video.py VIDEO [--output DIR] [--sign NAME]
```

- `VIDEO`: Path to video file
- `--output, -o`: Output directory (default: `backend/animations/keyframes`)
- `--sign, -s`: Sign name (default: parent folder name)

### batch_process_videos.py

```bash
python scripts/batch_process_videos.py [OPTIONS]
```

- `--train-dir`: Training directory (default: `train`)
- `--output-dir`: Output directory (default: `backend/animations/keyframes`)
- `--limit N`: Process only first N signs
- `--phase {1,2,3,all}`: Processing phase (default: `all`)
- `--category NAME`: Specific category (e.g., `phase1_numbers`)

## 📈 Examples

Process just numbers:

```bash
python scripts/batch_process_videos.py --category phase1_numbers
```

Process first 10 signs:

```bash
python scripts/batch_process_videos.py --limit 10
```

Process specific sign:

```bash
python scripts/extract_pose_from_video.py train/hello/hello_1.mp4 --sign hello
```

## 🎨 Integration with Avatar

After processing, update `avatar_3d.js` to load the animations:

```javascript
// Load external animations
fetch('/static/animations/asl_animations.js')
    .then(response => response.text())
    .then(code => {
        eval(code);
        // ASL_ANIMATIONS is now available
    });
```

Or manually copy JavaScript code from individual extractions.

## ⚙️ How It Works

1. **Video Input**: Reads MP4 training videos
2. **MediaPipe Processing**: Detects 21 hand landmarks + body pose
3. **Keyframe Sampling**: Extracts every 5th frame
4. **Coordinate Mapping**: Converts MediaPipe coords (0-1) to avatar space
5. **Finger Curl Calculation**: Computes curl values (0=extended, 1=closed)
6. **JSON Export**: Saves animation data
7. **JavaScript Generation**: Creates code for avatar_3d.js

## 📊 Expected Results

- **Processing Time**: ~2-3 seconds per video
- **Keyframes**: 10-30 per sign (depending on duration)
- **File Size**: ~2-5 KB per JSON file
- **Total Size**: ~1-3 MB for all 648 animations

## 🐛 Troubleshooting

**MediaPipe not found:**

```bash
conda install -c conda-forge mediapipe opencv
```

**Video not opening:**

- Check video path
- Ensure video is valid MP4
- Try with different video from same folder

**No hand detected:**

- Video quality may be poor
- Hand may be out of frame
- Try different video sample

**Permission errors:**

- Run with appropriate permissions
- Check output directory is writable

## 📝 Notes

- First video in each folder is used as reference
- Right hand is primary (most ASL signs)
- Left hand data also extracted for two-handed signs
- Animations can be manually refined after extraction
