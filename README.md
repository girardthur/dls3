# DLS3 - Application Django

Application Django 5.2.8 avec Python 3.11

## Démarrage avec Docker

### Prérequis
- Docker
- Docker Compose

### Installation et lancement

1. **Construire et démarrer les conteneurs**
   ```bash
   docker-compose up --build
   ```

2. **Accéder à l'application**
   - Application Django : http://localhost:8000
   - Base de données PostgreSQL : localhost:5432

3. **Exécuter les migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Créer un superutilisateur**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Commandes utiles

- **Arrêter les conteneurs**
  ```bash
  docker-compose down
  ```

- **Voir les logs**
  ```bash
  docker-compose logs -f web
  ```

- **Exécuter des commandes Django**
  ```bash
  docker-compose exec web python manage.py <commande>
  ```

- **Accéder au shell Django**
  ```bash
  docker-compose exec web python manage.py shell
  ```

## Développement sans Docker

### Installation

1. **Créer et activer l'environnement virtuel**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   # ou
   venv\Scripts\activate  # Sur Windows
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Exécuter les migrations**
   ```bash
   python manage.py migrate
   ```

4. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

## Structure du projet

```
dls3/
├── config/              # Configuration Django
├── manage.py            # Script de gestion Django
├── requirements.txt     # Dépendances Python
├── Dockerfile          # Configuration Docker
├── docker-compose.yml  # Orchestration Docker
└── .env.example        # Variables d'environnement d'exemple
```
