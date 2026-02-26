import pymysql
from flask import current_app

def get_db_connection():
    """Créer une connexion à la base de données MySQL"""
    try:
        connection = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DATABASE'],
            port=current_app.config['MYSQL_PORT'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        import traceback
        traceback.print_exc()
        return None
