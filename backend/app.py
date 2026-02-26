import os
import sys
import traceback

try:
    import logging
    from datetime import timedelta
    from flask import Flask, session
    from dotenv import load_dotenv

    # Add project root to path to allow imports from backend
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from backend.config import config
    from backend.server.routes import bp as main_bp

    load_dotenv()
except Exception as e:
    with open(os.path.join(os.path.dirname(__file__), 'crash.txt'), 'w') as f:
        f.write("ERREUR D'IMPORTATION / INITIALISATION :\n")
        f.write(traceback.format_exc())
    print("CRASH LOGGED TO crash.txt")
    sys.exit(1)

# Configuration du logging
handlers = [
    logging.FileHandler('server_debug.log'),
    logging.StreamHandler()
]
logging.basicConfig(level=logging.DEBUG, handlers=handlers,
                    format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__)

# Charger la configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Configuration de la session
app.permanent_session_lifetime = timedelta(hours=1)

@app.before_request
def make_session_permanent():
    session.permanent = True

# Créer les dossiers nécessaires
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('backend/static/audio', exist_ok=True) # Ensure static/audio exists

# Enregistrer le Blueprint
app.register_blueprint(main_bp)

if __name__ == '__main__':
    from backend.utils.predict import load_model
    try:
        load_model()
    except Exception as e:
        print(f"Warning: Could not load model at startup: {e}")

    print("="*50)
    print("Démarrage du serveur...")
    print("L'application est accessible à l'adresse : http://127.0.0.1:5000")
    print("="*50)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print("\n" + "!"*50)
        print("ERREUR FATALE LORS DU LANCEMENT :")
        print(e)
        print("!"*50 + "\n")
