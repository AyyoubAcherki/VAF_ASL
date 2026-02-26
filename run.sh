#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ -d ".venv" ]; then
    echo "Activation de l'environnement virtuel..."
    source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
else
    echo "Avertissement : Aucun environnement virtuel (.venv) trouvé."
fi

cd backend
echo "Installation des dépendances..."
python -m pip install -r requirements.txt

echo ""
echo "Démarrage de l'application Flask..."
echo ""
echo "L'application sera disponible sur: http://127.0.0.1:5000"
echo ""

python app.py
