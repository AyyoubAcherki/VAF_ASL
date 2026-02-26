from flask import Blueprint, render_template, request, jsonify, send_from_directory, session, redirect, url_for, flash, current_app
import os
import time
import json
import logging
import base64
import io
import tempfile
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from PIL import Image

try:
    import librosa
    import matplotlib.pyplot as plt
    import librosa.display
    HAS_TRAINING_LIBS = True
except ImportError:
    HAS_TRAINING_LIBS = False

from backend.database import get_db_connection
from backend.utils.predict import predict_image_file, load_model, ASL_CLASSES
from backend.utils.preprocess import preprocess_image
from backend.utils.predict_video import predict_video_sequence, load_cnn_lstm_model

bp = Blueprint('main', __name__)

# Helper helper
def save_prediction(user_email, prediction_type, predicted_class, confidence, input_data=None):
    """Enregistrer une prédiction dans la base de données"""
    if not user_email:
        logging.error("Erreur: user_email est None dans save_prediction")
        return False
    
    conn = get_db_connection()
    if not conn:
        logging.error("Erreur: Impossible de se connecter à la base de données dans save_prediction")
        return False
    
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO predictions (user_email, prediction_type, predicted_class, confidence, input_data)
                VALUES (%s, %s, %s, %s, %s)
            """
            input_data_json = json.dumps(input_data) if input_data else None
            logging.debug(f"Exécution SQL: {sql} avec {(user_email, prediction_type, predicted_class, confidence, input_data_json)}")
            cursor.execute(sql, (user_email, prediction_type, predicted_class, confidence, input_data_json))
            conn.commit()
            logging.info(f"Prédiction enregistrée: {predicted_class} ({prediction_type}) pour {user_email}")
            return True
    except Exception as e:
        logging.error(f"Erreur lors de l'enregistrement de la prédiction: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# Décorateur pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            # Pour les requêtes AJAX, retourner une erreur JSON au lieu de rediriger
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Non authentifié'}), 401
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.context_processor
def inject_user_profile():
    """Injecter les infos de profil dans tous les templates"""
    if 'user_email' in session:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    sql = "SELECT first_name, last_name, profile_image FROM users WHERE email = %s"
                    cursor.execute(sql, (session['user_email'],))
                    user = cursor.fetchone()
                    if user:
                        return {'current_user_profile': user}
            except Exception:
                pass
            finally:
                conn.close()
    return {'current_user_profile': None}

# ===== ROUTES D'AUTHENTIFICATION =====

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Veuillez remplir tous les champs', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Erreur de connexion à la base de données', 'error')
            return render_template('login.html')
        
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email = %s AND is_active = TRUE"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session.permanent = True
                    session['user_email'] = user['email']
                    session['user_name'] = user.get('first_name', 'User')
                    
                    # Mettre à jour la dernière connexion
                    update_sql = "UPDATE users SET last_login = %s WHERE email = %s"
                    cursor.execute(update_sql, (datetime.now(), email))
                    conn.commit()
                    
                    flash('Connexion réussie!', 'success')
                    return redirect(url_for('main.index'))
                else:
                    flash('Email ou mot de passe incorrect', 'error')
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            flash('Erreur lors de la connexion', 'error')
        finally:
            conn.close()
    
    return render_template('login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if not email or not password or not confirm_password:
            flash('Veuillez remplir tous les champs obligatoires', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return render_template('signup.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Erreur de connexion à la base de données', 'error')
            return render_template('signup.html')
        
        try:
            with conn.cursor() as cursor:
                # Vérifier si l'email existe déjà
                sql = "SELECT email FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                if cursor.fetchone():
                    flash('Cet email est déjà utilisé', 'error')
                    return render_template('signup.html')
                
                # Créer le nouvel utilisateur
                password_hash = generate_password_hash(password)
                insert_sql = """
                    INSERT INTO users (email, password_hash, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (email, password_hash, first_name, last_name))
                conn.commit()
                
                flash('Inscription réussie! Vous pouvez maintenant vous connecter', 'success')
                return redirect(url_for('main.login'))
        except Exception as e:
            print(f"Erreur lors de l'inscription: {e}")
            flash('Erreur lors de l\'inscription', 'error')
            conn.rollback()
        finally:
            conn.close()
    
    return render_template('signup.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile_page():
    """Page de profil utilisateur"""
    user_email = session.get('user_email')
    conn = get_db_connection()
    if not conn:
        flash('Erreur de connexion à la base de données', 'error')
        return redirect(url_for('main.index'))
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (user_email,))
            user_info = cursor.fetchone()
            
            if not user_info:
                flash('Utilisateur non trouvé', 'error')
                return redirect(url_for('main.index'))
            
            return render_template('profile.html', 
                                 user_email=user_email,
                                 user_name=session.get('user_name', user_info.get('first_name', 'User')),
                                 user_info=user_info)
    except Exception as e:
        print(f"Erreur lors du chargement du profil: {e}")
        flash('Erreur lors du chargement du profil', 'error')
        return redirect(url_for('main.index'))
    finally:
        conn.close()

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Mettre à jour le profil utilisateur"""
    user_email = session.get('user_email')
    form_type = request.form.get('form_type')
    
    conn = get_db_connection()
    if not conn:
        flash('Erreur de connexion à la base de données', 'error')
        return redirect(url_for('main.profile_page'))
    
    try:
        with conn.cursor() as cursor:
            if form_type == 'info':
                # Mise à jour des informations
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()
                
                update_sql = """
                    UPDATE users 
                    SET first_name = %s, last_name = %s 
                    WHERE email = %s
                """
                cursor.execute(update_sql, (first_name, last_name, user_email))
                conn.commit()
                
                # Mettre à jour la session
                session['user_name'] = first_name or 'User'
                
                flash('Profil mis à jour avec succès!', 'success')
                
            elif form_type == 'password':
                # Changement de mot de passe
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_new_password')
                
                if not current_password or not new_password or not confirm_password:
                    flash('Veuillez remplir tous les champs', 'error')
                    return redirect(url_for('main.profile_page'))
                
                if new_password != confirm_password:
                    flash('Les nouveaux mots de passe ne correspondent pas', 'error')
                    return redirect(url_for('main.profile_page'))
                
                if len(new_password) < 6:
                    flash('Le nouveau mot de passe doit contenir au moins 6 caractères', 'error')
                    return redirect(url_for('main.profile_page'))
                
                # Vérifier le mot de passe actuel
                sql = "SELECT password_hash FROM users WHERE email = %s"
                cursor.execute(sql, (user_email,))
                user = cursor.fetchone()
                
                if not user or not check_password_hash(user['password_hash'], current_password):
                    flash('Mot de passe actuel incorrect', 'error')
                    return redirect(url_for('main.profile_page'))
                
                # Mettre à jour le mot de passe
                new_password_hash = generate_password_hash(new_password)
                update_sql = "UPDATE users SET password_hash = %s WHERE email = %s"
                cursor.execute(update_sql, (new_password_hash, user_email))
                conn.commit()
                
                flash('Mot de passe modifié avec succès!', 'success')
            
            elif form_type == 'image':
                # Mise à jour de la photo de profil
                if 'profile_image' not in request.files:
                    flash('Aucun fichier sélectionné', 'error')
                    return redirect(url_for('main.profile_page'))
                
                file = request.files['profile_image']
                if file.filename == '':
                    flash('Aucun fichier sélectionné', 'error')
                    return redirect(url_for('main.profile_page'))
                
                if file:
                    filename = secure_filename(f"profile_{int(time.time())}_{file.filename}")
                    # Ensure directory exists
                    profile_pics_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_pics')
                    os.makedirs(profile_pics_dir, exist_ok=True)
                    
                    filepath = os.path.join(profile_pics_dir, filename)
                    file.save(filepath)
                    
                    # Update DB (store relative path for serving)
                    relative_path = f"uploads/profile_pics/{filename}"
                    update_sql = "UPDATE users SET profile_image = %s WHERE email = %s"
                    cursor.execute(update_sql, (relative_path, user_email))
                    conn.commit()
                    
                    flash('Photo de profil mise à jour!', 'success')

    except Exception as e:
        print(f"Erreur lors de la mise à jour du profil: {e}")
        flash('Erreur lors de la mise à jour', 'error')
        conn.rollback()
    finally:
        conn.close()
    
    return redirect(url_for('main.profile_page'))

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/api/profile/stats')
@login_required
def api_profile_stats():
    """API pour obtenir les statistiques du profil"""
    user_email = session.get('user_email')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion'}), 500
    
    try:
        with conn.cursor() as cursor:
            # Nombre de prédictions
            sql = "SELECT COUNT(*) as total FROM predictions WHERE user_email = %s"
            cursor.execute(sql, (user_email,))
            predictions = cursor.fetchone()
            
            # Date d'inscription
            sql = "SELECT created_at FROM users WHERE email = %s"
            cursor.execute(sql, (user_email,))
            user = cursor.fetchone()
            
            return jsonify({
                'total_predictions': predictions['total'] if predictions else 0,
                'member_since': user['created_at'].isoformat() if user and user['created_at'] else None
            })
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ===== ROUTES PRINCIPALES =====

@bp.route('/')
def index():
    return render_template('index.html', user_email=session.get('user_email'))

@bp.route('/predict')
@login_required
def predict_page():
    return render_template('predict.html', user_email=session.get('user_email'))

@bp.route('/predict_online')
@login_required
def predict_online_page():
    return render_template('predict_online.html', user_email=session.get('user_email'))

@bp.route('/audio_translate')
@login_required
def audio_translate_page():
    return render_template('audio_translate.html', user_email=session.get('user_email'))

@bp.route('/quiz')
@login_required
def quiz_page():
    # Path relative to project root
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    images = []
    if os.path.exists(images_dir):
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                class_name = filename.replace('asl_', '').replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
                images.append({
                    'filename': filename,
                    'class': class_name.upper() if class_name not in ['del', 'nothing', 'space'] else class_name
                })
    return render_template('quiz.html', images=images, user_email=session.get('user_email'))


@bp.route('/education')
def education_page():
    # Path relative to project root
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    images_data = []
    if os.path.exists(images_dir):
        for filename in sorted(os.listdir(images_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                class_name = filename.replace('asl_', '').replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
                if class_name in ['del', 'nothing', 'space']:
                    if class_name == 'del':
                        meaning = 'Supprimer / Delete'
                    elif class_name == 'nothing':
                        meaning = 'Rien / Nothing'
                    else:
                        meaning = 'Espace / Space'
                else:
                    meaning = f'Lettre {class_name.upper()}'
                
                images_data.append({
                    'filename': filename,
                    'class': class_name.upper() if class_name not in ['del', 'nothing', 'space'] else class_name,
                    'meaning': meaning
                })
    return render_template('education.html', images_data=images_data, user_email=session.get('user_email'))

@bp.route('/analytics')
@login_required
def analytics_page():
    return render_template('analytics.html', user_email=session.get('user_email'))

# ===== APIs =====

@bp.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """API pour prédire une image uploadée"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'Non authentifié'}), 401
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            result = predict_image_file(filepath)
            
            if result:
                # Enregistrer la prédiction
                save_prediction(
                    user_email=user_email,
                    prediction_type='image',
                    predicted_class=result['class'],
                    confidence=result['confidence'],
                    input_data={'filename': filename}
                )
                
                os.remove(filepath)
                return jsonify(result)
            else:
                return jsonify({'error': 'Erreur lors de la prédiction'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/predict_base64', methods=['POST'])
@login_required
def api_predict_base64():
    """API pour prédire une image en base64 (webcam)"""
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({'error': 'Aucune image fournie'}), 400
        
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'Non authentifié'}), 401
        
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        img_array = np.array(image)
        processed_img = preprocess_image(img_array)
        model = load_model()
        predictions = model.predict(processed_img, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        predicted_class = ASL_CLASSES[predicted_class_idx]
        
        # Enregistrer la prédiction (optionnel pour webcam, peut être fait périodiquement)
        save_prediction_enabled = data.get('save', False)
        if save_prediction_enabled:
            save_prediction(
                user_email=user_email,
                prediction_type='webcam',
                predicted_class=predicted_class,
                confidence=confidence,
                input_data={'source': 'webcam'}
            )
        
        return jsonify({
            'class': predicted_class,
            'confidence': confidence
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/predict_video', methods=['POST'])
@login_required
def api_predict_video():
    """API pour prédire une séquence vidéo (mots ASL)"""
    try:
        data = request.json
        if 'frames' not in data:
            return jsonify({'error': 'Aucune séquence de frames fournie'}), 400
        
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'Non authentifié'}), 401
        
        # Décoder les frames base64
        frames_data = data['frames']
        frames = []
        
        for frame_b64 in frames_data:
            if ',' in frame_b64:
                frame_b64 = frame_b64.split(',')[1]
            frame_bytes = base64.b64decode(frame_b64)
            frame_image = Image.open(io.BytesIO(frame_bytes))
            frames.append(np.array(frame_image))
        
        # Convertir en numpy array
        video_frames = np.array(frames)
        
        # Faire la prédiction
        result = predict_video_sequence(video_frames)
        
        if result:
            # Enregistrer la prédiction
            save_prediction_enabled = data.get('save', True)
            if save_prediction_enabled:
                save_prediction(
                    user_email=user_email,
                    prediction_type='video',
                    predicted_class=result['word'],
                    confidence=result['confidence'],
                    input_data={'source': 'video', 'num_frames': len(frames)}
                )
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Erreur lors de la prédiction vidéo'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/gloss_to_sentence', methods=['POST'])
@login_required
def api_gloss_to_sentence():
    """API pour convertir des gloss ASL en phrase complète via LLM"""
    from backend.utils.predict_video import asl_gloss_to_sentence
    
    try:
        data = request.json
        words = data.get('words', [])
        lang = data.get('lang', 'fr') # Par défaut français pour l'interface
        
        if not words:
             return jsonify({'sentence': ''})
             
        # Appel à Ollama via la fonction utilitaire
        sentence = asl_gloss_to_sentence(words, lang)
        
        return jsonify({
            'original_gloss': words,
            'sentence': sentence,
            'lang': lang
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/audio_to_text', methods=['POST'])
@login_required
def api_audio_to_text():
    """Convertir l'audio en texte"""
    # Configurer le chemin FFmpeg si nécessaire (Windows)
    ffmpeg_path = current_app.config.get('FFMPEG_PATH', os.environ.get('FFMPEG_PATH', 'C:\\ffmpeg\\bin'))
    if os.path.exists(ffmpeg_path):
        ffmpeg_exe = os.path.join(ffmpeg_path, 'ffmpeg.exe')
        ffprobe_exe = os.path.join(ffmpeg_path, 'ffprobe.exe')
        if os.path.exists(ffmpeg_exe):
            AudioSegment.converter = ffmpeg_exe
        if os.path.exists(ffprobe_exe):
            AudioSegment.ffprobe = ffprobe_exe
    
    tmp_file_path = None
    wav_file_path = None
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Aucun fichier audio fourni'}), 400
        
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'Non authentifié'}), 401
        
        audio_file = request.files['audio']
        filename = audio_file.filename
        file_ext = os.path.splitext(filename)[1].lower() if filename else '.wav'
        
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Convertir en WAV si nécessaire
        wav_file_path = tmp_file_path
        try:
            # Essayer d'abord de lire directement comme WAV
            with sr.AudioFile(tmp_file_path) as source:
                pass  # Test si c'est un WAV valide
        except Exception:
            # Si ce n'est pas un WAV, convertir
            try:
                # Déterminer le format
                if file_ext in ['.mp3', '.mpeg']:
                    audio_segment = AudioSegment.from_mp3(tmp_file_path)
                elif file_ext in ['.ogg', '.oga']:
                    audio_segment = AudioSegment.from_ogg(tmp_file_path)
                elif file_ext in ['.webm']:
                    audio_segment = AudioSegment.from_file(tmp_file_path, format='webm')
                elif file_ext in ['.m4a', '.aac']:
                    audio_segment = AudioSegment.from_file(tmp_file_path, format='m4a')
                elif file_ext in ['.flac']:
                    audio_segment = AudioSegment.from_file(tmp_file_path, format='flac')
                else:
                    # Essayer de détecter automatiquement le format
                    audio_segment = AudioSegment.from_file(tmp_file_path)
                
                # Convertir en WAV mono 16kHz (format requis par SpeechRecognition)
                audio_segment = audio_segment.set_channels(1)  # Mono
                audio_segment = audio_segment.set_frame_rate(16000)  # 16kHz
                audio_segment = audio_segment.set_sample_width(2)  # 16-bit
                
                # Sauvegarder en WAV
                wav_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
                audio_segment.export(wav_file_path, format='wav')
                
            except Exception as e:
                error_msg = str(e)
                # Vérifier si c'est une erreur liée à ffmpeg
                if 'ffmpeg' in error_msg.lower() or 'ffprobe' in error_msg.lower() or 'not found' in error_msg.lower():
                    return jsonify({
                        'error': 'La conversion audio nécessite ffmpeg. Veuillez installer ffmpeg ou utiliser un fichier WAV. Voir INSTALL_FFMPEG.md pour les instructions.'
                    }), 400
                else:
                    return jsonify({
                        'error': f'Format audio non supporté ou erreur de conversion: {error_msg}. Formats supportés: WAV, MP3, OGG, WebM, M4A, FLAC. Pour les formats autres que WAV, ffmpeg doit être installé.'
                    }), 400
        
        # Reconnaissance vocale
        r = sr.Recognizer()
        
        # Ajuster les paramètres pour une meilleure reconnaissance
        r.energy_threshold = 300  # Réduire le seuil d'énergie pour capter plus de sons
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8  # Temps de pause avant de considérer la fin de la parole
        
        try:
            with sr.AudioFile(wav_file_path) as source:
                # Ajuster le bruit ambiant
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio = r.record(source)
                
                # Vérifier si l'audio contient du son
                if len(audio.frame_data) == 0:
                    return jsonify({'error': 'Le fichier audio est vide ou trop court'}), 400
                    
        except Exception as e:
            return jsonify({'error': f'Erreur lors de la lecture du fichier audio: {str(e)}'}), 400
        
        # Reconnaissance avec plusieurs tentatives
        try:
            text = None
            errors = []
            
            # Tentative 1: Français
            try:
                text = r.recognize_google(audio, language='fr-FR')
                logging.info(f"Reconnaissance réussie en français: {text}")
            except sr.UnknownValueError:
                errors.append("Français: audio non reconnu")
                # Tentative 2: Anglais
                try:
                    text = r.recognize_google(audio, language='en-US')
                    logging.info(f"Reconnaissance réussie en anglais: {text}")
                except sr.UnknownValueError:
                    errors.append("Anglais: audio non reconnu")
                    # Tentative 3: Arabe (si applicable)
                    try:
                        text = r.recognize_google(audio, language='ar-MA')
                        logging.info(f"Reconnaissance réussie en arabe: {text}")
                    except sr.UnknownValueError:
                        errors.append("Arabe (MA): audio non reconnu")
                        # Tentative 4: Arabe Standard (SA)
                        try:
                            text = r.recognize_google(audio, language='ar-SA')
                            logging.info(f"Reconnaissance réussie en arabe standard: {text}")
                        except sr.UnknownValueError:
                            errors.append("Arabe (SA): audio non reconnu")
            except sr.RequestError as e:
                logging.error(f"Erreur de service Google: {e}")
                return jsonify({'error': f'Erreur du service de reconnaissance: {e}. Vérifiez votre connexion internet.'}), 500
            
            if text:
                return jsonify({'text': text})
            else:
                error_details = " | ".join(errors)
                return jsonify({
                    'error': 'Impossible de reconnaître l\'audio dans aucune langue testée.',
                    'details': error_details,
                    'suggestions': [
                        'Parlez plus clairement et distinctement',
                        'Assurez-vous que le microphone fonctionne correctement',
                        'Réduisez le bruit de fond',
                        'Parlez plus fort',
                        'Essayez d\'enregistrer un audio plus long (au moins 1-2 secondes)'
                    ]
                }), 400
                
        except sr.RequestError as e:
            logging.error(f"Erreur de requête: {e}")
            return jsonify({'error': f'Erreur du service de reconnaissance: {e}. Vérifiez votre connexion internet.'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors du traitement audio: {str(e)}'}), 500
    finally:
        # Nettoyer les fichiers temporaires
        for file_path in [tmp_file_path, wav_file_path]:
            if file_path and os.path.exists(file_path) and file_path != tmp_file_path:
                try:
                    os.remove(file_path)
                except:
                    pass
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except:
                pass

@bp.route('/api/text_to_signs', methods=['POST'])
@login_required
def api_text_to_signs():
    """Convertir le texte en séquence de signes ASL"""
    try:
        data = request.json
        text = data.get('text', '').upper()
        user_email = session.get('user_email')
        
        signs = []
        for char in text:
            if char == ' ':
                signs.append('space')
            elif char.isalpha():
                signs.append(char)
            else:
                continue
        
        # Enregistrer les prédictions audio
        if user_email and signs:
            for sign in signs:
                if sign in ASL_CLASSES:
                    save_prediction(
                        user_email=user_email,
                        prediction_type='audio',
                        predicted_class=sign,
                        confidence=1.0,  # Confiance par défaut pour audio
                        input_data={'text': text, 'sign': sign}
                    )
        
        return jsonify({'signs': signs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/audio/translate/asl', methods=['POST'])
@login_required
def api_audio_translate_asl():
    """
    Enhanced audio translation with CNN-LSTM ASL prediction
    Combines audio-to-text and text-to-ASL in one endpoint
    """
    print("DEBUG: Entered api_audio_translate_asl") # Debugging print
    from backend.utils.predict_video import predict_text_to_asl
    
    # Configurer le chemin FFmpeg si nécessaire
    ffmpeg_path = current_app.config.get('FFMPEG_PATH', os.environ.get('FFMPEG_PATH', 'C:\\ffmpeg\\bin'))
    if os.path.exists(ffmpeg_path):
        ffmpeg_exe = os.path.join(ffmpeg_path, 'ffmpeg.exe')
        ffprobe_exe = os.path.join(ffmpeg_path, 'ffprobe.exe')
        if os.path.exists(ffmpeg_exe):
            AudioSegment.converter = ffmpeg_exe
        if os.path.exists(ffprobe_exe):
            AudioSegment.ffprobe = ffprobe_exe
    
    tmp_file_path = None
    wav_file_path = None
    
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Aucun fichier audio fourni'}), 400
        
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'Non authentifié'}), 401
        
        audio_file = request.files['audio']
        filename = audio_file.filename
        file_ext = os.path.splitext(filename)[1].lower() if filename else '.wav'
        
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Convertir en WAV si nécessaire
        wav_file_path = tmp_file_path
        try:
            with sr.AudioFile(tmp_file_path) as source:
                pass  # Test si c'est un WAV valide
        except Exception:
            # Convertir en WAV
            try:
                if file_ext in ['.mp3', '.mpeg']:
                    audio_segment = AudioSegment.from_mp3(tmp_file_path)
                elif file_ext in ['.ogg', '.oga']:
                    audio_segment = AudioSegment.from_ogg(tmp_file_path)
                elif file_ext in ['.webm']:
                    audio_segment = AudioSegment.from_file(tmp_file_path, format='webm')
                elif file_ext in ['.m4a', '.aac']:
                    audio_segment = AudioSegment.from_file(tmp_file_path, format='m4a')
                elif file_ext in ['.flac']:
                    audio_segment = AudioSegment.from_file(tmp_file_path, format='flac')
                else:
                    audio_segment = AudioSegment.from_file(tmp_file_path)
                
                audio_segment = audio_segment.set_channels(1)
                audio_segment = audio_segment.set_frame_rate(16000)
                audio_segment = audio_segment.set_sample_width(2)
                
                wav_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
                audio_segment.export(wav_file_path, format='wav')
            except Exception as e:
                error_msg = str(e)
                if 'ffmpeg' in error_msg.lower():
                    return jsonify({'error': 'FFmpeg requis pour ce format audio'}), 400
                return jsonify({'error': f'Erreur de conversion audio: {error_msg}'}), 400
        
        # Reconnaissance vocale
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        
        try:
            with sr.AudioFile(wav_file_path) as source:
                
                # Log duration
                duration = source.DURATION
                logging.info(f"Audio file duration: {duration:.2f}s")
                print(f"DEBUG: Audio duration: {duration:.2f}s") # Debugging
                
                # Reduce ambient noise adjustment to avoid cutting off early speech
                # For pre-recorded files, this is often unnecessary or should be very short
                r.adjust_for_ambient_noise(source, duration=0.1)
                audio = r.record(source)
                
                if not audio or len(audio.frame_data) == 0:
                    logging.warning("Audio data is empty")
                    return jsonify({'error': 'Le fichier audio est vide'}), 400
        except Exception as e:
            logging.error(f"Erreur de lecture audio debug: {str(e)}")
            print(f"DEBUG: Error reading audio: {e}") # Debugging
            return jsonify({'error': f'Erreur de lecture audio: {str(e)}'}), 400
        
        # Reconnaissance multi-langue
        text = None
        detected_language = None
        
        try:
            # Français
            try:
                print("DEBUG: Attempting Google Recognition (FR)...") # Debugging
                text = r.recognize_google(audio, language='fr-FR')
                detected_language = 'fr'
                logging.info(f"Reconnaissance FR: {text}")
                print(f"DEBUG: Recognized text: {text}") # Debugging
            except sr.UnknownValueError:
                # Anglais
                try:
                    text = r.recognize_google(audio, language='en-US')
                    detected_language = 'en'
                    logging.info(f"Reconnaissance EN: {text}")
                except sr.UnknownValueError:
                    # Arabe
                    try:
                        text = r.recognize_google(audio, language='ar-MA')
                        detected_language = 'ar'
                        logging.info(f"Reconnaissance AR: {text}")
                    except sr.UnknownValueError:
                        logging.debug("Reconnaissance AR échouée")
                        pass
            except sr.RequestError as e:
                return jsonify({'error': f'Erreur du service de reconnaissance: {e}'}), 500
            
            if not text:
                return jsonify({
                    'error': 'Impossible de reconnaître l\'audio',
                    'suggestions': [
                        'Parlez plus clairement',
                        'Réduisez le bruit de fond',
                        'Enregistrez un audio plus long'
                    ]
                }), 400
            
            # Prédiction ASL avec support des phrases complètes
            asl_result = predict_text_to_asl(text, apply_grammar=True)
            words = text.split()
            
            # Format de réponse amélioré
            word_details = asl_result.get('word_details', [])
            asl_sequence = asl_result.get('asl_sequence', [])
            
            # Statistiques pour compatibilité
            found_words = sum(1 for w in word_details if w.get('status') in ['found', 'phrase_match'])
            unknown_words = sum(1 for w in word_details if w.get('status') == 'unknown')
            
            response_data = {
                'text': text,
                'detected_language': detected_language,
                'prediction_type': asl_result.get('type', 'word_by_word'),
                'asl_sequence': asl_sequence,
                'grammar_type': asl_result.get('grammar_type', 'none'),
                'confidence': asl_result.get('confidence', 0.6),
                'word_details': word_details,
                # Aliases for frontend compatibility
                'asl_predictions': word_details,
                'total_words': len(words),
                'found_words': found_words,
                'unknown_words': unknown_words
            }
            
            # Ajouter les marqueurs non-manuels si présents
            if 'non_manual' in asl_result and asl_result['non_manual']:
                response_data['non_manual_markers'] = asl_result['non_manual']
            
            # Ajouter le pattern correspondant si c'est une phrase
            if asl_result.get('type') == 'phrase':
                response_data['matched_phrase'] = asl_result.get('matched_pattern', '')
            
            return jsonify(response_data)
            
        except sr.RequestError as e:
            logging.error(f"Erreur de requête: {e}")
            return jsonify({'error': f'Erreur du service: {e}'}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur: {str(e)}'}), 500
    finally:
        # Nettoyer les fichiers temporaires
        for file_path in [tmp_file_path, wav_file_path]:
            if file_path and os.path.exists(file_path) and file_path != tmp_file_path:
                try:
                    os.remove(file_path)
                except:
                    pass
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except:
                pass

@bp.route('/api/analytics/stats')
@login_required
def api_analytics_stats():
    """Obtenir les statistiques pour l'utilisateur"""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Non authentifié'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
    
    try:
        with conn.cursor() as cursor:
            # Statistiques générales
            stats_sql = """
                SELECT 
                    COUNT(*) as total_predictions,
                    AVG(confidence) as avg_confidence,
                    prediction_type,
                    COUNT(DISTINCT predicted_class) as unique_classes
                FROM predictions
                WHERE user_email = %s
                GROUP BY prediction_type
            """
            cursor.execute(stats_sql, (user_email,))
            stats = cursor.fetchall()
            
            # Prédictions par classe
            classes_sql = """
                SELECT 
                    predicted_class,
                    COUNT(*) as count,
                    AVG(confidence) as avg_confidence
                FROM predictions
                WHERE user_email = %s
                GROUP BY predicted_class
                ORDER BY count DESC
            """
            cursor.execute(classes_sql, (user_email,))
            classes = cursor.fetchall()
            
            # Prédictions par jour
            daily_sql = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM predictions
                WHERE user_email = %s
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """
            cursor.execute(daily_sql, (user_email,))
            daily = cursor.fetchall()
            
            return jsonify({
                'stats': stats,
                'classes': classes,
                'daily': daily
            })
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@bp.route('/api/quiz/start_session', methods=['POST'])
@login_required
def api_quiz_start_session():
    """Initialise une nouvelle session de quiz"""
    user_email = session.get('user_email')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO quiz_results 
                (user_email, total_questions, correct_answers, score_percentage, quiz_duration, questions_data)
                VALUES (%s, 0, 0, 0, 0, '[]')
            """
            cursor.execute(sql, (user_email,))
            conn.commit()
            inserted_id = cursor.lastrowid
            logging.info(f"Session de quiz démarrée pour {user_email}, ID: {inserted_id}")
            return jsonify({'success': True, 'quiz_id': inserted_id})
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation du quiz: {e}")
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@bp.route('/api/quiz/update_progress', methods=['POST'])
@login_required
def api_quiz_update_progress():
    """Met à jour le progrès du quiz après chaque question"""
    try:
        data = request.json
        quiz_id = data.get('quiz_id')
        question_data = data.get('question_data')  # Un seul objet de question
        
        if not quiz_id or not question_data:
            return jsonify({'error': 'ID de quiz ou données de question manquants'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        try:
            with conn.cursor() as cursor:
                # 1. Récupérer les données actuelles
                cursor.execute("SELECT questions_data, correct_answers, total_questions FROM quiz_results WHERE id = %s", (quiz_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Quiz non trouvé'}), 404
                
                current_questions = json.loads(row['questions_data']) if row['questions_data'] else []
                current_correct = row['correct_answers'] or 0
                current_total = row['total_questions'] or 0
                
                # 2. Mettre à jour avec la nouvelle question
                current_questions.append(question_data)
                new_total = current_total + 1
                new_correct = current_correct + (1 if question_data.get('correct') else 0)
                new_percentage = (new_correct / new_total * 100) if new_total > 0 else 0
                
                # 3. Sauvegarder
                sql = """
                    UPDATE quiz_results 
                    SET total_questions = %s, 
                    correct_answers = %s, 
                    score_percentage = %s, 
                    questions_data = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (
                    new_total,
                    new_correct,
                    new_percentage,
                    json.dumps(current_questions),
                    quiz_id
                ))
                conn.commit()
                return jsonify({'success': True, 'current_score': new_correct, 'total': new_total})
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour du quiz: {e}")
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def api_quiz_save_result_legacy(data, user_email):
    """Ancienne méthode si le frontend n'envoie pas de quiz_id (compatibilité)"""
    total_questions = data.get('total_questions', 0)
    correct_answers = data.get('correct_answers', 0)
    score_percentage = data.get('score_percentage', 0)
    quiz_duration = data.get('quiz_duration', 0)
    questions_data = data.get('questions_data', [])
    
    conn = get_db_connection()
    if not conn: return jsonify({'error': 'DB Error'}), 500
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO quiz_results (user_email, total_questions, correct_answers, score_percentage, quiz_duration, questions_data) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (user_email, total_questions, correct_answers, score_percentage, quiz_duration, json.dumps(questions_data)))
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@bp.route('/api/quiz/save_result', methods=['POST'])
@login_required
def api_quiz_save_result():
    """Finalise un résultat de quiz (mise à jour de la durée finale)"""
    user_email = session.get('user_email')
    
    try:
        data = request.json
        quiz_id = data.get('quiz_id')
        quiz_duration = data.get('quiz_duration', 0)
        
        if not quiz_id:
            # Fallback pour l'ancien système si pas de quiz_id
            return api_quiz_save_result_legacy(data, user_email)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE quiz_results SET quiz_duration = %s WHERE id = %s"
                cursor.execute(sql, (quiz_duration, quiz_id))
                conn.commit()
                logging.info(f"Quiz {quiz_id} finalisé pour {user_email}")
                return jsonify({'success': True})
        except Exception as e:
            logging.error(f"Erreur lors de la finalisation du quiz: {e}")
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/quiz/analysis')
@login_required
def api_quiz_analysis():
    """API pour obtenir l'analyse des résultats de quiz"""
    user_email = session.get('user_email')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
    
    try:
        with conn.cursor() as cursor:
            # Statistiques générales
            stats_sql = """
                SELECT 
                    COUNT(*) as total_quizzes,
                    AVG(score_percentage) as avg_score,
                    MAX(score_percentage) as best_score,
                    MIN(score_percentage) as worst_score,
                    SUM(correct_answers) as total_correct,
                    SUM(total_questions) as total_questions,
                    AVG(quiz_duration) as avg_duration
                FROM quiz_results
                WHERE user_email = %s
            """
            cursor.execute(stats_sql, (user_email,))
            stats = cursor.fetchone()
            
            # Si aucune donnée, initialiser stats avec des zéros
            if not stats or stats.get('total_quizzes') == 0:
                stats = {
                    'total_quizzes': 0,
                    'avg_score': 0,
                    'best_score': 0,
                    'worst_score': 0,
                    'total_correct': 0,
                    'total_questions': 0,
                    'avg_duration': 0
                }

            # Résultats par date (30 derniers jours)
            daily_sql = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count,
                    AVG(score_percentage) as avg_score
                FROM quiz_results
                WHERE user_email = %s
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """
            cursor.execute(daily_sql, (user_email,))
            daily = cursor.fetchall()
            
            # Distribution des scores
            score_distribution_sql = """
                SELECT 
                    CASE 
                        WHEN score_percentage >= 90 THEN 'Excellent (90-100%%)'
                        WHEN score_percentage >= 70 THEN 'Très bien (70-89%%)'
                        WHEN score_percentage >= 50 THEN 'Bien (50-69%%)'
                        ELSE 'À améliorer (<50%%)'
                    END as score_range,
                    COUNT(*) as count
                FROM quiz_results
                WHERE user_email = %s
                GROUP BY score_range
            """
            cursor.execute(score_distribution_sql, (user_email,))
            score_distribution = cursor.fetchall()
            
            # Derniers résultats
            recent_sql = """
                SELECT 
                    id, total_questions, correct_answers, score_percentage, quiz_duration, created_at
                FROM quiz_results
                WHERE user_email = %s
                ORDER BY created_at DESC
                LIMIT 10
            """
            cursor.execute(recent_sql, (user_email,))
            recent = cursor.fetchall()
            
            # Analyse des erreurs
            errors_sql = "SELECT questions_data FROM quiz_results WHERE user_email = %s ORDER BY created_at DESC LIMIT 50"
            cursor.execute(errors_sql, (user_email,))
            all_questions = cursor.fetchall()
            
            error_analysis = {}
            total_predictions_by_sign = {}
            correct_predictions = {}

            for row in all_questions:
                if row['questions_data']:
                    try:
                        q_list = json.loads(row['questions_data']) if isinstance(row['questions_data'], str) else row['questions_data']
                        for q in q_list:
                            sign = q.get('correct_answer', 'Unknown')
                            total_predictions_by_sign[sign] = total_predictions_by_sign.get(sign, 0) + 1
                            if q.get('correct', False):
                                correct_predictions[sign] = correct_predictions.get(sign, 0) + 1
                            else:
                                error_analysis[sign] = error_analysis.get(sign, 0) + 1
                    except Exception as e:
                        logging.warning(f"Failed to parse questions_data: {e}")
            
            top_errors = sorted(error_analysis.items(), key=lambda x: x[1], reverse=True)[:10]
            
            prediction_accuracy = []
            for sign, total in total_predictions_by_sign.items():
                correct = correct_predictions.get(sign, 0)
                accuracy = (correct / total * 100) if total > 0 else 0
                prediction_accuracy.append({
                    'sign': sign,
                    'total': total,
                    'correct': correct,
                    'accuracy': round(accuracy, 1)
                })
            prediction_accuracy.sort(key=lambda x: x['accuracy'], reverse=True)
            
            daily_formatted = []
            for d in daily:
                date_str = str(d['date']) if d.get('date') else ''
                daily_formatted.append({
                    'date': date_str,
                    'count': d.get('count', 0),
                    'avg_score': float(d['avg_score']) if d.get('avg_score') is not None else 0
                })
            
            recent_formatted = []
            for r in recent:
                recent_formatted.append({
                    'id': r['id'],
                    'total_questions': r['total_questions'],
                    'correct_answers': r['correct_answers'],
                    'score_percentage': float(r['score_percentage']),
                    'quiz_duration': r['quiz_duration'] or 0,
                    'created_at': r['created_at'].isoformat() if hasattr(r['created_at'], 'isoformat') else str(r['created_at'])
                })
            
            return jsonify({
                'stats': {
                    'total_quizzes': stats.get('total_quizzes', 0),
                    'avg_score': float(stats['avg_score']) if stats.get('avg_score') is not None else 0,
                    'best_score': float(stats['best_score']) if stats.get('best_score') is not None else 0,
                    'worst_score': float(stats['worst_score']) if stats.get('worst_score') is not None else 0,
                    'total_correct': stats.get('total_correct', 0) or 0,
                    'total_questions': stats.get('total_questions', 0) or 0,
                    'avg_duration': float(stats['avg_duration']) if stats.get('avg_duration') is not None else 0
                },
                'daily': daily_formatted,
                'score_distribution': score_distribution,
                'recent': recent_formatted,
                'top_errors': [{'sign': sign, 'count': count} for sign, count in top_errors],
                'prediction_accuracy': prediction_accuracy[:15]
            })
    except Exception as e:
        logging.error(f"Erreur lors de l'analyse des quiz: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@bp.route('/api/powerbi/export')
@login_required
def api_powerbi_export():
    """API pour exporter les données vers PowerBI"""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Non authentifié'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
    
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    id,
                    user_email,
                    prediction_type,
                    predicted_class,
                    confidence,
                    created_at,
                    input_data
                FROM predictions
                WHERE user_email = %s
                ORDER BY created_at DESC
            """
            cursor.execute(sql, (user_email,))
            data = cursor.fetchall()
            
            # Convertir les données pour PowerBI
            powerbi_data = []
            for row in data:
                powerbi_data.append({
                    'id': row['id'],
                    'user_email': row['user_email'],
                    'prediction_type': row['prediction_type'],
                    'predicted_class': row['predicted_class'],
                    'confidence': float(row['confidence']),
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'input_data': row['input_data']
                })
            
            return jsonify({
                'data': powerbi_data,
                'total': len(powerbi_data)
            })
    except Exception as e:
        print(f"Erreur lors de l'export PowerBI: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@bp.route('/api/training/save', methods=['POST'])
@login_required
def api_training_save():
    """Sauvegarde un échantillon audio et son spectrogramme pour l'entraînement"""
    if not HAS_TRAINING_LIBS:
        return jsonify({'error': 'Bibliothèques d\'entraînement non disponibles sur le serveur'}), 501
    
    try:
        if 'audio' not in request.files or 'word' not in request.form:
            return jsonify({'error': 'Audio ou mot manquant'}), 400
            
        audio_file = request.files['audio']
        word = request.form['word'].upper()
        
        # 1. Créer les dossiers
        # Path updated for new structure (relative to backend)
        # ../training/dataset
        training_path = os.path.join(current_app.root_path, '..', 'training', 'dataset')
        audio_dir = os.path.join(training_path, 'audio')
        spectrograms_dir = os.path.join(training_path, 'spectrograms')
        
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(spectrograms_dir, exist_ok=True)
        
        # 2. Sauvegarder l'audio
        timestamp = int(time.time())
        audio_filename = f"{word}_{timestamp}.wav"
        audio_path = os.path.join(audio_dir, audio_filename)
        audio_file.save(audio_path)
        
        # 3. Générer le spectrogramme
        spec_filename = f"{word}_{timestamp}.png"
        spec_path = os.path.join(spectrograms_dir, spec_filename)
        
        try:
            y, sr_rate = librosa.load(audio_path)
            S = librosa.feature.melspectrogram(y=y, sr=sr_rate, n_mels=128)
            S_dB = librosa.power_to_db(S, ref=np.max)
            
            plt.figure(figsize=(10, 4))
            librosa.display.specshow(S_dB, sr=sr_rate)
            plt.axis('off')
            plt.savefig(spec_path, bbox_inches='tight', pad_inches=0)
            plt.close()
        except Exception as e:
            logging.error(f"Erreur lors de la génération du spectrogramme: {e}")
            return jsonify({'error': f'Erreur spectrogramme: {str(e)}'}), 500
        
        # 4. Enregistrer en base de données
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erreur DB'}), 500
            
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO asl_training_labels (word, audio_path, spectrogram_path) VALUES (%s, %s, %s)"
                cursor.execute(sql, (word, audio_path, spec_path))
                conn.commit()
                logging.info(f"Échantillon d'entraînement ajouté pour '{word}'")
            return jsonify({
                'success': True, 
                'message': f'Échantillon pour "{word}" sauvegardé',
                'spec_path': spec_path
            })
        except Exception as e:
            logging.error(f"Erreur SQL training save: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
        
    except Exception as e:
        logging.error(f"Erreur training save générale: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/images/<filename>')
def serve_image(filename):
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    return send_from_directory(images_dir, filename)



@bp.route('/conversation')
@login_required
def conversation_page():
    """Page du Pont de Conversation bidirectionnel"""
    pass # No import needed
    current_user_profile = None
    if 'user_email' in session:
        # Note: Using get_db_connection pattern usually, but here adapting to what was likely there
        # or simplified version if no ORM
        # For now, let's use the session data or basic query if needed
        # Assuming direct DB connection is preferred based on other routes
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE email = %s", (session['user_email'],))
                    user = cursor.fetchone()
                    if user:
                        current_user_profile = {
                            'email': user['email'],
                            'name': user.get('first_name', 'User'),
                            'profile_image': user.get('profile_image')
                        }
            finally:
                conn.close()
                
    return render_template('conversation.html', current_user_profile=current_user_profile)

@bp.route('/api/video/<word>')
def serve_video_sign(word):
    """Serve the ASL video for a specific word"""
    try:
        # Normalize word
        word = word.lower().strip()
        
        # Path to train directory (relative to backend/server/routes.py -> ../../train)
        # current_app.root_path points to backend/
        train_dir = os.path.join(current_app.root_path, '..', 'train')
        word_dir = os.path.join(train_dir, word)
        
        if not os.path.exists(word_dir):
            return jsonify({'error': 'Word not found'}), 404
            
        # Find first mp4 file
        video_file = None
        for filename in os.listdir(word_dir):
            if filename.lower().endswith('.mp4'):
                video_file = filename
                break
                
        if not video_file:
            return jsonify({'error': 'No video for this word'}), 404
            
        return send_from_directory(word_dir, video_file)
        
    except Exception as e:
        logging.error(f"Error serving video: {e}")
        return jsonify({'error': str(e)}), 500
