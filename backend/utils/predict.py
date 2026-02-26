from tensorflow import keras
import numpy as np
import os
from .preprocess import preprocess_image

# Path relative to backend/utils/ -> backend/model/asl_model.h5
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model', 'asl_model.h5')

model = None

# Classes ASL (29 classes)
ASL_CLASSES = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'del', 'nothing', 'space'
]

def load_model():
    global model
    if model is None:
        try:
            model = keras.models.load_model(MODEL_PATH)
            print("Modèle chargé avec succès!")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {e}")
    return model

def predict_image_file(image_path):
    """Prédire la classe d'une image"""
    try:
        model = load_model()
        processed_img = preprocess_image(image_path)
        predictions = model.predict(processed_img, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        predicted_class = ASL_CLASSES[predicted_class_idx]
        
        return {
            'class': predicted_class,
            'confidence': confidence,
            'all_predictions': {
                ASL_CLASSES[i]: float(predictions[0][i]) 
                for i in range(len(ASL_CLASSES))
            }
        }
    except Exception as e:
        print(f"Erreur lors de la prédiction: {e}")
        return None
