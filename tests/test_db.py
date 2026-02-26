import pymysql
import os

# Paramètres du script (identiques à app.py)
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '1234567890'
MYSQL_DATABASE = 'asl_recognition'

print(f"Tentative de connexion à {MYSQL_DATABASE} sur {MYSQL_HOST}...")

try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connexion réussie!")
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        print(f"Nombre d'utilisateurs: {result['count']}")
    conn.close()
except Exception as e:
    print(f"ERREUR: {e}")
