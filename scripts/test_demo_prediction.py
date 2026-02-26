
import sys
import os
import json

# Ajouter le chemin du projet pour l'import
sys.path.append(os.getcwd())

from backend.utils.predict_video import predict_text_to_asl, ASL_WORDS
from backend.utils.asl_phrases import ASL_PHRASES

def test_predictions():
    test_inputs = [
        "bonjour",
        "comment ça va",
        "nice to meet you",
        "je t'aime",
        "i need help",
        "manger pomme" # Word by word
    ]
    
    print("=== DÉMONSTRATION DES PRÉDICTIONS ASL ===\n")
    
    for text in test_inputs:
        print(f"Entrée: '{text}'")
        result = predict_text_to_asl(text)
        
        print(f"Type: {result['type']}")
        print(f"Séquence ASL: {' -> '.join(result['asl_sequence'])}")
        if 'matched_pattern' in result:
            print(f"Pattern: {result['matched_pattern']}")
        print("-" * 30)

    print(f"\nTotal mots (classes): {len(ASL_WORDS)}")
    print(f"Total phrases pré-définies: {len(ASL_PHRASES)}")

if __name__ == "__main__":
    test_predictions()
