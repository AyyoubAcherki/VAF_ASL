# Guide de Configuration de la Base de Données MySQL

Ce guide explique comment configurer la base de données MySQL pour l'application ASL Recognition.

## 📋 Prérequis

- MySQL Server installé (version 5.7 ou supérieure)
- Python avec PyMySQL installé
- Accès administrateur à MySQL

## 🚀 Installation

### 1. Installer MySQL

**Windows:**
- Téléchargez MySQL depuis https://dev.mysql.com/downloads/mysql/
- Installez MySQL Server
- Notez le mot de passe root

**Linux:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
```

**macOS:**
```bash
brew install mysql
```

### 2. Créer la Base de Données

1. **Connectez-vous à MySQL:**
```bash
mysql -u root -p
```

2. **Exécutez le script SQL:**
```bash
mysql -u root -p < database.sql
```

Ou exécutez les commandes manuellement:

```sql
CREATE DATABASE IF NOT EXISTS asl_recognition CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE asl_recognition;

-- Copiez le contenu de database.sql ici
```

### 3. Créer un Utilisateur (Optionnel mais Recommandé)

```sql
CREATE USER 'asl_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON asl_recognition.* TO 'asl_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configurer l'Application

1. **Modifiez `config.py`:**
```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '1234567890'
MYSQL_DATABASE = 'asl_recognition'
MYSQL_PORT = 3306
```

2. **Ou utilisez des variables d'environnement:**
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=asl_user
export MYSQL_PASSWORD=votre_mot_de_passe
export MYSQL_DATABASE=asl_recognition
export MYSQL_PORT=3306
```

### 5. Tester la Connexion

```python
python -c "from app import get_db_connection; conn = get_db_connection(); print('Connexion réussie!' if conn else 'Erreur de connexion'); conn.close() if conn else None"
```

## 📊 Structure de la Base de Données

### Table: users
- `email` (VARCHAR(255), PRIMARY KEY): Email de l'utilisateur
- `password_hash` (VARCHAR(255)): Hash du mot de passe
- `first_name` (VARCHAR(100)): Prénom
- `last_name` (VARCHAR(100)): Nom
- `created_at` (TIMESTAMP): Date de création
- `last_login` (TIMESTAMP): Dernière connexion
- `is_active` (BOOLEAN): Statut actif/inactif

### Table: predictions
- `id` (INT, AUTO_INCREMENT, PRIMARY KEY): ID de la prédiction
- `user_email` (VARCHAR(255), FOREIGN KEY): Email de l'utilisateur
- `prediction_type` (ENUM): Type de prédiction (image, webcam, audio)
- `predicted_class` (VARCHAR(50)): Classe prédite
- `confidence` (DECIMAL(5,4)): Niveau de confiance
- `input_data` (TEXT): Données d'entrée (JSON)
- `created_at` (TIMESTAMP): Date de création

### Table: user_sessions (Optionnel)
- `session_id` (VARCHAR(255), PRIMARY KEY): ID de session
- `user_email` (VARCHAR(255), FOREIGN KEY): Email de l'utilisateur
- `created_at` (TIMESTAMP): Date de création
- `expires_at` (TIMESTAMP): Date d'expiration

### Table: quiz_results
- `id` (INT, AUTO_INCREMENT, PRIMARY KEY): ID du résultat
- `user_email` (VARCHAR(255), FOREIGN KEY): Email de l'utilisateur
- `total_questions` (INT): Nombre total de questions
- `correct_answers` (INT): Nombre de bonnes réponses
- `score_percentage` (DECIMAL(5,2)): Score en pourcentage
- `quiz_duration` (INT): Durée du quiz en secondes
- `questions_data` (TEXT): Détails des questions (JSON)
- `created_at` (TIMESTAMP): Date de création

## 🔧 Maintenance

### Sauvegarder la Base de Données

```bash
mysqldump -u root -p asl_recognition > backup.sql
```

### Restaurer la Base de Données

```bash
mysql -u root -p asl_recognition < backup.sql
```

### Vérifier les Tables

```sql
USE asl_recognition;
SHOW TABLES;
DESCRIBE users;
DESCRIBE predictions;
```

### Vérifier les Données

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM predictions;
SELECT * FROM users LIMIT 10;
SELECT * FROM predictions LIMIT 10;
```

## 🐛 Dépannage

### Erreur de connexion
- Vérifiez que MySQL est en cours d'exécution
- Vérifiez les credentials dans `config.py`
- Vérifiez les permissions de l'utilisateur

### Erreur "Table doesn't exist"
- Exécutez le script `database.sql`
- Vérifiez que vous utilisez la bonne base de données

### Erreur "Access denied"
- Vérifiez le mot de passe
- Vérifiez les permissions de l'utilisateur
- Vérifiez que l'utilisateur peut se connecter depuis localhost

### Erreur de caractères
- Vérifiez que la base de données utilise utf8mb4
- Vérifiez les collations des tables

## 📝 Notes

- Utilisez toujours des mots de passe forts en production
- Faites des sauvegardes régulières
- Surveillez les performances de la base de données
- Utilisez des index pour améliorer les performances

## 🔐 Sécurité

1. **Ne commitez jamais les mots de passe**
   - Utilisez des variables d'environnement
   - Utilisez un fichier `.env` (non versionné)

2. **Limitez les permissions**
   - Créez un utilisateur avec des permissions minimales
   - Ne donnez pas tous les privilèges sauf si nécessaire

3. **Utilisez des connexions sécurisées**
   - Utilisez SSL pour les connexions MySQL
   - Chiffrez les mots de passe

4. **Surveillez les accès**
   - Activez les logs MySQL
   - Surveillez les tentatives de connexion

---

Pour plus d'informations, consultez la documentation MySQL: https://dev.mysql.com/doc/
