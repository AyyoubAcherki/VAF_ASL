"""
Module pour la prédiction vidéo ASL avec le modèle CNN-LSTM
"""
import os
import re
import numpy as np
from tensorflow import keras
import logging
import json
import requests

# Configuration Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Modèle par défaut, peut être changé

def asl_gloss_to_sentence(words, lang="fr"):
    """
    Convertir une suite de mots (Gloss ASL) en phrase naturelle via LLM (Ollama)
    """
    if not words:
        return ""
        
    gloss_text = ", ".join(words)
    
    prompt = f"""
You are a professional ASL interpreter.
Convert ASL GLOSS to a natural sentence in {lang}.
Do NOT add words.
Do NOT explain.
Do NOT hallucinate.
Keep grammar natural.

Examples:

ASL GLOSS:
HELLO
Output:
Hello.

ASL GLOSS:
ME STUDENT
Output:
I am a student.

ASL GLOSS:
YOU NAME WHAT
Output:
What is your name?

Now convert:

ASL GLOSS:
{gloss_text}
Output:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3 # Plus déterministe
                }
            },
            timeout=10 # Timeout court pour éviter de bloquer l'UI trop longtemps
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip().replace('"', '')
        else:
            logging.error(f"Ollama Error {response.status_code}: {response.text}")
            return gloss_text # Fallback: retour brut
            
    except Exception as e:
        logging.error(f"Erreur connexion Ollama: {e}")
        return gloss_text # Fallback


# Chemin vers le modèle CNN-LSTM
CNN_LSTM_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model', 'cnn_lstm_words_aug_best.h5')

# Classes de mots ASL - Vocabulaire complet du modèle CNN-LSTM
# Ces mots correspondent aux classes que le modèle a été entraîné à reconnaître
# Charger les classes depuis le fichier JSON
MSASL_CLASSES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'MSASL_classes.json')

try:
    with open(MSASL_CLASSES_PATH, 'r') as f:
        ASL_WORDS = json.load(f)
    logging.info(f"✅ Loaded {len(ASL_WORDS)} classes from MSASL_classes.json")
except Exception as e:
    logging.error(f"⚠️ Error loading MSASL_classes.json: {e}")
    # Fallback minimal list if file missing
    ASL_WORDS = ["hello", "yes", "no", "thanks", "please", "i", "you", "me"] 

# Charger les mappings depuis les fichiers JSON
def load_json_translations(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Erreur lors du chargement de {filename}: {e}")
    return {}

FRENCH_TO_ENGLISH = load_json_translations('translations_fr.json')
ARABIC_TO_ENGLISH = load_json_translations('translations_ar.json')

# Variable globale pour le modèle
cnn_lstm_model = None

def load_cnn_lstm_model():
    """Charger le modèle CNN-LSTM pour la reconnaissance vidéo"""
    global cnn_lstm_model
    if cnn_lstm_model is None:
        try:
            if os.path.exists(CNN_LSTM_MODEL_PATH):
                cnn_lstm_model = keras.models.load_model(CNN_LSTM_MODEL_PATH)
                logging.info(f"Modèle CNN-LSTM chargé avec succès depuis {CNN_LSTM_MODEL_PATH}")
            else:
                logging.warning(f"Modèle CNN-LSTM non trouvé à {CNN_LSTM_MODEL_PATH}")
        except Exception as e:
            logging.error(f"Erreur lors du chargement du modèle CNN-LSTM: {e}")
    return cnn_lstm_model

def preprocess_text(text):
    """
    Prétraiter le texte complet avant tokenisation
    """
    text = text.lower().strip()
    
    # Remplacer les expressions multi-mots courantes par des versions simples ou des tokens uniques
    multi_word_phrases = {
        # Français
        "s'il vous plaît": "svp",
        "sil vous plait": "svp",
        "s'il vous plait": "svp",
        "est-ce que": "",
        "tout le monde": "tout_le_monde",
        "en retard": "en_retard",
        "aujourd'hui": "aujourdhui",
        "d'accord": "daccord",
        "comment ça va": "how_are_you",
        "comment ca va": "how_are_you",
        "je t'aime": "i_love_you",
        "je taime": "i_love_you",
        "au revoir": "goodbye",
        
        # Arabe
        "السلام عليكم": "hello",
        "كيف حالك": "how_are_you",
        "مرة أخرى": "again",
        "ابن عم": "cousin",
        "ابنة الأخ": "niece",
        "ابن الأخ": "nephew",
        "بعد الظهر": "afternoon",
        "صباح الخير": "good_morning",
        "مساء الخير": "good_afternoon",
        "الحمد لله": "fine",  # Souvent utilisé pour dire 'bien'
    }
    
    for phrase, replacement in multi_word_phrases.items():
        text = text.replace(phrase, replacement)
        
    return text

def preprocess_word(word):
    """
    Prétraiter un mot pour la correspondance ASL
    """
    # Nettoyer le mot
    word = word.lower().strip()
    
    # Mapping additionnel pour les tokens spéciaux issus de preprocess_text
    special_mappings = {
        'daccord': 'ok',
        'aujourdhui': 'today',
        'en_retard': 'late',
        'how_are_you': 'how are you',
        'i_love_you': 'i love you',
        'good_morning': 'good morning',
        'good_afternoon': 'good afternoon',
        'svp': 'please'
    }
    
    if word in special_mappings:
        return special_mappings[word]
        
    # Retirer la ponctuation pour les mots simples
    word = re.sub(r'[^\w\s]', '', word)
    
    # Mapping additionnel pour les mots nettoyés s'ils ne sont pas dans special_mappings
    if word == 'sil': return 'please'
    
    # Essayer de traduire depuis le français
    if word in FRENCH_TO_ENGLISH:
        return FRENCH_TO_ENGLISH[word]
    
    # Essayer de traduire depuis l'arabe
    if word in ARABIC_TO_ENGLISH:
        word = ARABIC_TO_ENGLISH[word]
    
    # Fallback pour les mots courants qui ont un équivalent proche dans le vocabulaire
    if word == "you":
        return "your"
    if word == "i":
        word = "me"
    
    # Remplacer les espaces par des underscores pour matcher les labels du dossier train
    word = word.replace(' ', '_')
    
    # Gestion des préfixes arabes courants (أ، ال، ...) si le mot exact n'est pas trouvé
    if len(word) > 2:
        # Si le mot commence par 'ال' (Al-)
        if word.startswith('ال'):
            radical = word[2:]
            if radical in ARABIC_TO_ENGLISH:
                return ARABIC_TO_ENGLISH[radical]
        # Si le mot commence par 'أ' (souvent pour 'Je' or prefixe)
        if word.startswith('أ'):
            radical = word[1:]
            if radical in ARABIC_TO_ENGLISH:
                return ARABIC_TO_ENGLISH[radical]
        # Si le mot commence par 'و' (et)
    # Règles manuelles pour les mots courants (Anglais -> ASL Class)
    manual_corrections = {
        'yes': 'yes',
        'oui': 'yes',
        'si': 'yes',
        'no': 'no',
        'non': 'no',
        'hello': 'hello',
        'bonjour': 'hello',
        'salut': 'hello',
        'hi': 'hello',
        'thanks': 'thanks',
        'merci': 'thanks',
        'please': 'please',
        'svp': 'please',
        'i': 'i',
        'je': 'i',
        'me': 'me',
        'moi': 'me',
        'you': 'you',
        'tu': 'you',
        'vous': 'you',
        'toi': 'you'
        # Ajouter d'autres corrections ici
    }
    
    if word in manual_corrections:
        return manual_corrections[word]

    return word.lower()

def predict_text_to_asl(text, apply_grammar=True):
    """
    Convertir un texte complet en séquence de mots ASL avec support des phrases complètes
    
    Args:
        text: Texte d'entrée (français, anglais ou arabe)
        apply_grammar: Appliquer les règles de grammaire ASL
        
    Returns:
        list: Résultats de prédiction avec séquences ASL
    """
    try:
        # Import des modules de phrases et grammaire
        from .asl_phrases import get_phrase_match
        from .asl_grammar import detect_sentence_type, apply_asl_grammar, add_non_manual_markers, optimize_sign_sequence
    except ImportError:
        # Fallback si les modules ne sont pas disponibles
        logging.warning("Modules de phrases ASL non disponibles, utilisation du mode mot-par-mot")
        apply_grammar = False
    
    # Prétraiter le texte complet
    text_original = text
    text = preprocess_text(text)
    
    # Étape 1: Vérifier si c'est une phrase connue
    if apply_grammar:
        phrase_key, phrase_data = get_phrase_match(text)
        
        if phrase_data:
            # Phrase trouvée dans la base de données
            asl_sequence = phrase_data['asl_sequence']
            
            return {
                'type': 'phrase',
                'original_text': text_original,
                'matched_pattern': phrase_key,
                'asl_sequence': asl_sequence,
                'grammar_type': phrase_data['grammar'],
                'non_manual': phrase_data.get('non_manual'),
                'confidence': phrase_data.get('confidence', 1.0),
                'word_details': [
                    {
                        'original_word': text_original,
                        'asl_word': ' + '.join(asl_sequence),
                        'confidence': phrase_data.get('confidence', 1.0),
                        'status': 'phrase_match'
                    }
                ]
            }
    
    # Étape 2: Traduction mot par mot
    words = text.split()
    asl_words = []
    word_details = []
    
    for word in words:
        if not word:
            continue
        
        # Prétraiter le mot
        processed_word = preprocess_word(word)
        
        # Vérifier si le mot est dans le vocabulaire (insensible à la casse)
        # ASL_WORDS contient des mots en minuscules dans la définition vue plus haut, mais certains pourraient être différents.
        # On suppose que ASL_WORDS est une liste de strings.
        
        # Trouver le match exact dans ASL_WORDS (pour avoir la bonne casse du fichier)
        match = next((w for w in ASL_WORDS if w.lower() == processed_word.lower()), None)
        
        if match:
            asl_words.append(match) # Garder la casse originale de la classe
            word_details.append({
                'original_word': word,
                'asl_word': match, # Le mot clé pour la vidéo/avatar
                'confidence': 1.0,
                'status': 'found'
            })
        else:
            # Mot inconnu - Essayer le Mapping Sémantique via LLM
            # (Limiter pour éviter de surcharger Ollama si trop de mots)
            smart_match = smart_map_to_msasl(processed_word)
            
            if smart_match:
                asl_words.append(smart_match)
                word_details.append({
                    'original_word': word,
                    'asl_word': smart_match,
                    'confidence': 0.8, # Confiance un peu plus basse car c'est une approximation
                    'status': 'smart_mapped',
                    'mapped_from': processed_word
                })
            else:
                # Vraiment inconnu
                word_details.append({
                    'original_word': word,
                    'asl_word': None,
                    'confidence': 0.0,
                    'status': 'unknown',
                    'fallback': 'skipped'
                })

# Cache pour éviter de rapperler Ollama pour les mêmes mots
SMART_MAP_CACHE = {}

def smart_map_to_msasl(word):
    """
    Utilise Ollama pour trouver le mot le plus proche sémantiquement dans le vocabulaire MSASL (1000 mots).
    Ex: "Automobile" -> "car"
    """
    if not ASL_WORDS:
        return None
        
    # Vérifier le cache
    if word in SMART_MAP_CACHE:
        return SMART_MAP_CACHE[word]
        
    # Construire la liste des candidats (pour économiser des tokens, on pourrait en mettre moins, 
    # mais pour 1000 mots ça passe généralement dans le contexte de Llama3)
    vocab_str = ", ".join(ASL_WORDS)
    
    prompt = f"""
You are an ASL dictionary helper.
Target Vocabulary: [{vocab_str}]

Task: Find the word in the Target Vocabulary that has the CLOSEST meaning to the input word.
If the input word is a plural, noun, verb variant, or synonym, map it to the standard vocabulary word.
If NO close match exists, return "NONE".

Input: "{word}"
Best Match from Vocabulary (ONLY the word):"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1 # Très déterministe
                }
            },
            timeout=5 # Timeout court
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip().lower()
            
            # Nettoyer la réponse (parfois le LLM bavarde encore un peu malgré les instructions)
            # On vérifie si le résultat est vraiment dans notre liste
            clean_match = next((w for w in ASL_WORDS if w.lower() == result), None)
            
            if clean_match:
                SMART_MAP_CACHE[word] = clean_match
                logging.info(f"🧠 Smart Map: '{word}' -> '{clean_match}'")
                return clean_match
                
    except Exception as e:
        logging.error(f"Erreur Smart Map Ollama: {e}")
    
    # Si échec ou pas de match
    SMART_MAP_CACHE[word] = None
    return None
    
    # Étape 3: Appliquer les règles de grammaire ASL
    if apply_grammar and asl_words:
        sentence_type = detect_sentence_type(text_original)
        asl_words_reordered = apply_asl_grammar(asl_words, sentence_type)
        asl_words_optimized = optimize_sign_sequence(asl_words_reordered)
        non_manual_data = add_non_manual_markers(asl_words_optimized, sentence_type)
        
        return {
            'type': 'constructed',
            'original_text': text_original,
            'asl_sequence': asl_words_optimized,
            'grammar_type': sentence_type,
            'non_manual': non_manual_data.get('non_manual', []),
            'confidence': 0.7,  # Confiance plus faible pour les phrases construites
            'word_details': word_details
        }
    
    # Étape 4: Retour simple sans grammaire
    return {
        'type': 'word_by_word',
        'original_text': text_original,
        'asl_sequence': asl_words,
        'grammar_type': 'none',
        'confidence': 0.6,
        'word_details': word_details
    }


def predict_video_sequence(video_frames):
    """
    Prédire le mot ASL à partir d'une séquence de frames vidéo
    
    Args:
        video_frames: numpy array de shape (num_frames, height, width, channels)
        
    Returns:
        dict avec 'word', 'confidence', et 'all_predictions'
    """
    try:
        model = load_cnn_lstm_model()
        if model is None:
            return None
        
        # Prétraiter les frames si nécessaire
        processed_frames = preprocess_video_frames(video_frames)
        
        # Faire la prédiction
        predictions = model.predict(processed_frames, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_idx])
        
        # Vérifier que l'index est valide
        if predicted_idx < len(ASL_WORDS):
            predicted_word = ASL_WORDS[predicted_idx]
        else:
            predicted_word = f"Unknown_{predicted_idx}"
        
        return {
            'word': predicted_word,
            'confidence': confidence,
            'all_predictions': {
                ASL_WORDS[i]: float(predictions[0][i]) 
                for i in range(min(len(ASL_WORDS), len(predictions[0])))
            }
        }
    except Exception as e:
        logging.error(f"Erreur lors de la prédiction vidéo: {e}")
        import traceback
        traceback.print_exc()
        return None

def preprocess_video_frames(frames):
    """
    Prétraiter les frames vidéo pour le modèle (Batch, 40, 64, 64, 3)
    
    Args:
        frames: numpy array de frames (N, H, W, C)
        
    Returns:
        frames prétraitées et redimensionnées
    """
    import cv2
    
    processed_frames = []
    
    for frame in frames:
        # Redimensionner à 64x64 si nécessaire
        if frame.shape[0] != 64 or frame.shape[1] != 64:
            frame = cv2.resize(frame, (64, 64))
        processed_frames.append(frame)
    
    frames_array = np.array(processed_frames)
    
    # Normaliser les valeurs de pixels (0-255 -> 0-1)
    frames_array = frames_array.astype('float32') / 255.0
    
    # Ajouter la dimension batch si nécessaire
    if len(frames_array.shape) == 4:
        frames_array = np.expand_dims(frames_array, axis=0)
    
    return frames_array
