# Guide d'Authentification et Base de Données

Ce guide explique comment utiliser le système d'authentification et la base de données MySQL de l'application ASL Recognition.

## 🚀 Installation Rapide

### 1. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer la Base de Données MySQL

1. **Installer MySQL** (si ce n'est pas déjà fait)
2. **Créer la base de données:**
```bash
mysql -u root -p < database.sql
```

3. **Configurer les credentials** dans `config.py` ou utiliser des variables d'environnement:
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=votre_mot_de_passe
export MYSQL_DATABASE=asl_recognition
```

### 3. Démarrer l'Application

```bash
python app.py
```

## 🔐 Authentification

### Inscription

1. Allez sur `/signup`
2. Remplissez le formulaire:
   - Email (obligatoire, utilisé comme clé primaire)
   - Prénom (optionnel)
   - Nom (optionnel)
   - Mot de passe (minimum 6 caractères)
   - Confirmation du mot de passe
3. Cliquez sur "S'inscrire"

### Connexion

1. Allez sur `/login`
2. Entrez votre email et mot de passe
3. Cliquez sur "Se connecter"

### Déconnexion

1. Cliquez sur "Déconnexion" dans le menu
2. Ou allez sur `/logout`

## 📊 Enregistrement des Prédictions

Toutes les prédictions sont automatiquement enregistrées dans la base de données lorsque vous êtes connecté:

### Types de Prédictions

- **image**: Prédictions depuis l'upload d'images
- **webcam**: Prédictions depuis la webcam (lorsque vous cliquez sur "Capturer")
- **audio**: Prédictions depuis la traduction audio

### Données Enregistrées

Pour chaque prédiction:
- Email de l'utilisateur
- Type de prédiction
- Classe prédite
- Niveau de confiance
- Données d'entrée (JSON)
- Date et heure

## 📈 Page Analytics

La page Analytics (`/analytics`) affiche:

### Statistiques Générales
- Total des prédictions
- Confiance moyenne
- Nombre de types de prédictions
- Nombre de classes uniques

### Graphiques
- **Prédictions par type**: Graphique circulaire
- **Prédictions par classe**: Graphique en barres (top 10)
- **Prédictions par jour**: Graphique linéaire (30 derniers jours)
- **Confiance par type**: Graphique en barres

### Tableau des Prédictions
- Liste des 50 dernières prédictions
- Date, type, classe, confiance

## 🔗 API PowerBI

### Endpoint

```
GET /api/powerbi/export
```

### Réponse

```json
{
    "data": [
        {
            "id": 1,
            "user_email": "user@example.com",
            "prediction_type": "image",
            "predicted_class": "A",
            "confidence": 0.95,
            "created_at": "2024-01-01T12:00:00",
            "input_data": "{\"filename\": \"test.jpg\"}"
        }
    ],
    "total": 100
}
```

### Utilisation avec PowerBI

Voir le guide complet dans `POWERBI_GUIDE.md`

## 🗄️ Structure de la Base de Données

### Table: users
- `email` (PRIMARY KEY): Email de l'utilisateur
- `password_hash`: Hash du mot de passe
- `first_name`: Prénom
- `last_name`: Nom
- `created_at`: Date de création
- `last_login`: Dernière connexion
- `is_active`: Statut actif/inactif

### Table: predictions
- `id` (PRIMARY KEY): ID de la prédiction
- `user_email` (FOREIGN KEY): Email de l'utilisateur
- `prediction_type`: Type de prédiction (image, webcam, audio)
- `predicted_class`: Classe prédite
- `confidence`: Niveau de confiance (0-1)
- `input_data`: Données d'entrée (JSON)
- `created_at`: Date de création

## 🔒 Sécurité

### Mots de Passe
- Les mots de passe sont hashés avec Werkzeug
- Minimum 6 caractères requis
- Validation côté serveur et client

### Sessions
- Sessions Flask avec expiration (1 heure)
- Cookies sécurisés
- Protection CSRF (à implémenter en production)

### Base de Données
- Utilisez des mots de passe forts
- Ne commitez jamais les credentials
- Utilisez des variables d'environnement
- Activez SSL pour MySQL en production

## 🐛 Dépannage

### Erreur de connexion à la base de données
- Vérifiez que MySQL est en cours d'exécution
- Vérifiez les credentials dans `config.py`
- Vérifiez que la base de données existe
- Vérifiez les permissions de l'utilisateur

### Erreur "Email déjà utilisé"
- L'email est utilisé comme clé primaire
- Chaque email ne peut être utilisé qu'une fois
- Utilisez un autre email pour vous inscrire

### Erreur "Non authentifié"
- Vous devez être connecté pour accéder à certaines pages
- Connectez-vous d'abord
- Vérifiez que votre session n'a pas expiré

### Les prédictions ne sont pas enregistrées
- Vérifiez que vous êtes connecté
- Vérifiez les logs de l'application
- Vérifiez la connexion à la base de données
- Vérifiez les permissions de la table predictions

## 📝 Notes

- L'email est utilisé comme clé primaire (unique)
- Les prédictions sont liées à l'utilisateur via l'email
- Les données sont automatiquement nettoyées lors de la suppression d'un utilisateur (CASCADE)
- Les sessions expirent après 1 heure d'inactivité

## 🚀 Déploiement en Production

1. **Changez la clé secrète:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY') or 'changez-cette-cle-secrete'
```

2. **Utilisez HTTPS:**
- Configurez SSL/TLS
- Utilisez des cookies sécurisés

3. **Configurez MySQL:**
- Utilisez un utilisateur dédié
- Limitez les permissions
- Activez SSL

4. **Surveillez les logs:**
- Activez les logs d'erreur
- Surveillez les tentatives de connexion
- Surveillez les performances

---

Pour plus d'informations, consultez:
- `SETUP_DATABASE.md` pour la configuration de la base de données
- `POWERBI_GUIDE.md` pour l'intégration PowerBI

