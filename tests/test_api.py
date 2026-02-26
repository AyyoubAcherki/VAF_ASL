import requests
import json

# URL de l'API
url = 'http://localhost:5000/api/quiz/save_result'

# Données de test
quiz_data = {
    "total_questions": 5,
    "correct_answers": 4,
    "score_percentage": 80,
    "quiz_duration": 120,
    "questions_data": [
        {"question": "asl_a.jpg", "correct_answer": "A", "selected_answer": "A", "correct": True},
        {"question": "asl_b.jpg", "correct_answer": "B", "selected_answer": "C", "correct": False}
    ]
}

# Simuler une session (Cookie)
# NOTE: Dans un test réel, il faudrait d'abord se connecter.
# Mais comme j'ai temporairement retiré @login_required (ou si je le remets, je dois me connecter),
# je vais tester si l'insertion brute fonctionne si je passe un email valide si je modifie l'app.

print(f"Test d'envoi de données vers {url}...")
try:
    # On va tricher pour le test en utilisant un email de debug
    response = requests.post(url, json=quiz_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erreur: {e}")
