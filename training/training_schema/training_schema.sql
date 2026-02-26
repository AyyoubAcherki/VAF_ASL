-- Schéma pour la base de données d'entraînement ASL
USE asl_recognition;

CREATE TABLE IF NOT EXISTS asl_training_labels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    audio_path VARCHAR(255) NOT NULL,
    spectrogram_path VARCHAR(255),
    action_metadata JSON, -- Pour stocker les détails de l'animation si besoin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_word (word)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
