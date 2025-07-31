# NAIRA - Système d'authentification

Système d'authentification Django avec Argon2 et frontend Vue.js 3.

## Installation

### Option 1: Docker Compose (Recommandé)

```bash
# Démarrer tous les services (complet)
docker compose up -d

# Ou démarrer seulement l'authentification
docker compose -f docker-compose.dev.yml up -d

# Voir les logs
docker compose logs -f django frontend

# Arrêter les services
docker compose down
```

### Option 2: Installation locale

#### Backend Django

```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

#### Frontend Vue.js

```bash
# Installer pnpm (si pas déjà installé)
./install_pnpm.sh

# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
pnpm install

# Lancer le serveur de développement
pnpm dev
# ou utiliser le script automatique
./start_frontend.sh
```

## Tests

### Tests Backend
```bash
python manage.py test auth.tests
```

### Tests Frontend
```bash
cd frontend
pnpm test:run
```

### Tous les tests
```bash
./run_tests.sh
```

## Résumé des tests

### Tests Backend Django (27 tests) 
- **Argon2BackendTest** (9 tests) : Tests du backend d'authentification Argon2
- **AuthAPITest** (8 tests) : Tests de l'API REST d'authentification
- **AuthViewsTest** (7 tests) : Tests des vues d'authentification
- **ProfileModelTest** (3 tests) : Tests du modèle Profile

### Tests Frontend Vue.js (15 tests) 
- **Auth Store** : Tests du store Pinia pour l'authentification
- **Login** : Tests de connexion
- **Register** : Tests d'inscription
- **Logout** : Tests de déconnexion
- **Get Profile** : Tests de récupération de profil
- **Forgot Password** : Tests de récupération de mot de passe
- **Verify Email** : Tests de vérification d'email
- **Clear Error** : Tests de gestion d'erreurs

## Fonctionnalités implémentées

1. **Authentification Argon2** : Hachage sécurisé des mots de passe
2. **API REST complète** : Endpoints pour signup, login, logout, profile
3. **Frontend Vue.js 3** : Interface moderne avec Pinia et Vue Router
4. **Tests complets** : Couverture de test pour backend et frontend
5. **Gestion d'erreurs** : Messages d'erreur appropriés
6. **Validation** : Vérification des données d'entrée
7. **Sécurité** : Protection CSRF, validation des tokens

## Accès
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Admin Django: http://localhost:8000/admin

## Commandes utiles

### Docker
```bash
# Démarrer
docker compose -f docker-compose.dev.yml up -d

# Rebuilder les images
docker compose -f docker-compose.dev.yml build

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f

# Arrêter les services
docker compose -f docker-compose.dev.yml down

# Créer un superuser dans le conteneur
docker compose -f docker-compose.dev.yml exec django python manage.py createsuperuser
```

### Local
```bash
# Installation pnpm
./install_pnpm.sh

# Démarrage automatique frontend
./start_frontend.sh

# Migration base de données
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Lancer tous les tests
./run_tests.sh
``` 