# ASL Recognition Project

American Sign Language recognition web application with ML-powered predictions, user authentication, quiz system, and analytics.

## Project Structure

```
asl-project/
├── backend/           # Flask application
│   ├── app.py        # Main entry point
│   ├── config.py     # Configuration
│   ├── database.py   # Database utilities
│   ├── database.sql  # Database schema
│   ├── server/       # Routes (Blueprint)
│   ├── model/        # ML models
│   │   ├── asl_model.h5              # Image classification (letters)
│   │   └── cnn_lstm_words_aug_best.h5 # Video classification (words)
│   ├── utils/        # Preprocessing & prediction
│   │   ├── preprocess.py
│   │   ├── predict.py         # Image prediction
│   │   └── predict_video.py   # Video prediction
│   ├── static/       # CSS, JS, images
│   ├── templates/    # HTML templates
│   └── uploads/      # User uploads
├── training/         # Training data & scripts
│   ├── dataset/      # Audio & spectrograms
│   ├── scripts/      # Training scripts
│   └── training_schema/
├── tests/            # Test files
└── README.md
```

## Setup

### 1. Prerequisites

- Python 3.8+
- MySQL 8.0+
- FFmpeg (optional, for audio processing)

### 2. Database Setup

Create the database and tables:

```bash
mysql -u root -p < backend/database.sql
```

Or manually:

```sql
CREATE DATABASE asl_recognition CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then run the schema from `backend/database.sql`.

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=asl_recognition
MYSQL_PORT=3306
FFMPEG_PATH=C:\ffmpeg\bin
```

### 4. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Run the Application

```bash
python backend/app.py
```

The application will be available at `http://127.0.0.1:5000`

## Features

- 🔐 User authentication (signup/login)
- 🖼️ **Image-based ASL recognition** (letters A-Z)
- 📹 **Real-time webcam prediction** (letters)
- 🎥 **Video sequence recognition** (words) - NEW!
- 🎤 Audio-to-ASL translation
- 📝 Interactive quiz system
- 📊 Analytics dashboard
- 👤 User profiles with image upload

## Models

### 1. Image Classification Model (`asl_model.h5`)

- **Type**: CNN (Convolutional Neural Network)
- **Purpose**: Recognize ASL letters (A-Z) from static images
- **Input**: Single image (200x200 pixels)
- **Output**: Letter classification

### 2. Video Classification Model (`cnn_lstm_words_aug_best.h5`)

- **Type**: CNN-LSTM (Hybrid model)
- **Purpose**: Recognize ASL words from video sequences
- **Input**: Sequence of video frames
- **Output**: Word classification
- **Use case**: More complex signs that require motion

## API Endpoints

### Image Prediction

```
POST /api/predict
Content-Type: multipart/form-data
Body: file (image)
```

### Webcam Prediction

```
POST /api/predict_base64
Content-Type: application/json
Body: {"image": "base64_encoded_image"}
```

### Video Prediction (NEW)

```
POST /api/predict_video
Content-Type: application/json
Body: {"frames": ["base64_frame1", "base64_frame2", ...]}
```

## Documentation

- [Database Setup Guide](SETUP_DATABASE.md)
- [Authentication Guide](README_AUTH.md)
- [ASL Features](README_ASL.md)
- [PowerBI Integration](POWERBI_GUIDE.md)
- [FFmpeg Installation](INSTALL_FFMPEG.md)
