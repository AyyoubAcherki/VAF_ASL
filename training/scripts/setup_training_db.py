import os
import json
import pymysql
from dotenv import load_dotenv
import time

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import librosa
    import librosa.display
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False
    print("Note: librosa/matplotlib non installés. Spectrogrammes désactivés.")

load_dotenv()

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '1234567890'),
            database=os.getenv('MYSQL_DATABASE', 'asl_recognition'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"Erreur DB: {e}")
        return None

def init_training_db():
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            with open('training_schema.sql', 'r') as f:
                sql = f.read()
                for statement in sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
        conn.commit()
        print("Base de données d'entraînement initialisée.")
    except Exception as e:
        print(f"Erreur init: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_training_db()
    os.makedirs('dataset/audio', exist_ok=True)
    os.makedirs('dataset/spectrograms', exist_ok=True)
    print("Environnement d'entraînement prêt.")
