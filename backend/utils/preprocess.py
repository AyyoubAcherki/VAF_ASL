import numpy as np
from PIL import Image
import io

def preprocess_image(image):
    """Prétraiter l'image pour le modèle"""
    if isinstance(image, str):
        img = Image.open(image)
    else:
        # Assuming image is a numpy array or similar if not string
        try:
             img = Image.fromarray(image)
        except:
             # Fallback if it's already a PIL image
             img = image
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img = img.resize((64, 64))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array
