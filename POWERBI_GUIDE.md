# Guide de Connexion PowerBI

Ce guide explique comment connecter PowerBI à l'API de l'application ASL Recognition pour visualiser les données de prédictions.

## 🔗 URL de l'API PowerBI

```
http://votre-domaine/api/powerbi/export
```

## 📋 Étapes de Configuration

### 1. Obtenir l'URL de l'API

L'API retourne les données au format JSON avec la structure suivante:

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

### 2. Configuration dans PowerBI Desktop

1. **Ouvrir PowerBI Desktop**

2. **Obtenir les données**
   - Cliquez sur "Obtenir des données" (Get Data)
   - Sélectionnez "Web" (Web)
   - Entrez l'URL: `http://votre-domaine/api/powerbi/export`
   - Cliquez sur "OK"

3. **Authentification**
   - Sélectionnez "Anonyme" si l'API est publique
   - Ou configurez l'authentification si nécessaire (Basic, OAuth, etc.)

4. **Transformer les données**
   - PowerBI va charger les données JSON
   - Transformez la colonne `data` en table
   - Expandez les colonnes nécessaires

### 3. Configuration avec Authentification

Si votre API nécessite une authentification:

1. **Dans PowerBI Desktop**
   - Cliquez sur "Gérer les paramètres" (Manage Parameters)
   - Créez un paramètre pour le token d'authentification
   - Utilisez ce token dans les en-têtes HTTP

2. **Dans l'API Flask**
   - Vous pouvez ajouter un système de tokens API
   - Modifiez la route `/api/powerbi/export` pour accepter les tokens

### 4. Création de Visualisations

Une fois les données chargées, vous pouvez créer des visualisations:

- **Graphique en barres**: Nombre de prédictions par classe
- **Graphique circulaire**: Répartition par type de prédiction
- **Graphique linéaire**: Évolution dans le temps
- **Tableau**: Détails des prédictions

### 5. Actualisation des Données

Pour actualiser les données automatiquement:

1. **Dans PowerBI Desktop**
   - Allez dans "Actualiser" (Refresh)
   - Configurez l'actualisation programmée

2. **Dans PowerBI Service**
   - Configurez l'actualisation planifiée
   - Définissez la fréquence (quotidienne, hebdomadaire, etc.)

## 🔐 Authentification API (Optionnel)

Pour sécuriser l'API, vous pouvez ajouter un système de tokens:

### Modification de l'API

```python
@app.route('/api/powerbi/export')
@login_required  # Ou avec token API
def api_powerbi_export():
    # Votre code actuel
    pass
```

### Utilisation avec Token

1. Générer un token API pour l'utilisateur
2. Utiliser ce token dans les en-têtes HTTP de PowerBI
3. Vérifier le token dans l'API Flask

## 📊 Exemple de Requête

```bash
curl -X GET "http://localhost:5000/api/powerbi/export" \
  -H "Cookie: session=your_session_cookie"
```

## 🎯 Meilleures Pratiques

1. **Performance**
   - Limitez le nombre de résultats retournés
   - Ajoutez la pagination si nécessaire
   - Utilisez des index dans la base de données

2. **Sécurité**
   - Utilisez HTTPS en production
   - Implémentez l'authentification
   - Limitez le taux de requêtes (rate limiting)

3. **Données**
   - Nettoyez les données avant l'export
   - Formatez les dates correctement
   - Gérez les valeurs nulles

## 🚀 Déploiement

Pour utiliser l'API en production:

1. Déployez l'application Flask sur un serveur
2. Configurez un domaine
3. Activez HTTPS
4. Configurez l'authentification
5. Testez la connexion depuis PowerBI

## 📝 Notes

- L'API retourne uniquement les données de l'utilisateur connecté
- Les données sont triées par date (plus récentes en premier)
- La limite par défaut est de toutes les prédictions (vous pouvez ajouter une pagination)

## 🆘 Dépannage

### Erreur de connexion
- Vérifiez que l'application Flask est en cours d'exécution
- Vérifiez l'URL de l'API
- Vérifiez les paramètres de firewall

### Erreur d'authentification
- Vérifiez que vous êtes connecté
- Vérifiez la session Flask
- Vérifiez les cookies du navigateur

### Données vides
- Vérifiez qu'il y a des prédictions dans la base de données
- Vérifiez les logs de l'application
- Vérifiez les permissions de la base de données

---

Pour plus d'informations, consultez la documentation PowerBI: https://docs.microsoft.com/power-bi/

