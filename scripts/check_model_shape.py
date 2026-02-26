
import os
import tensorflow as tf
from tensorflow import keras

model_path = os.path.join('backend', 'model', 'cnn_lstm_words_aug_best.h5')
if os.path.exists(model_path):
    try:
        model = keras.models.load_model(model_path)
        print(f"Model Input Shape: {model.input_shape}")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print("Model not found")
