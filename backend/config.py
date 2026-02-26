# Configuration de l'application Flask
import os

class Config:
    """Configuration de base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Configuration MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '1234567890'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'asl_recognition'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    
    # Configuration Flask
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Configuration de session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure
    
    # Configuration FFmpeg (optionnel)
    FFMPEG_PATH = os.environ.get('FFMPEG_PATH', 'C:\\ffmpeg\\bin')

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

