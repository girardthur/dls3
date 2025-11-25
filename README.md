# DLS3 - Application Django

Application Django 5.2.8 avec Python 3.11

## Démarrage avec Docker

### Prérequis
- Docker
- Docker Compose

### Mode développement standalone

Pour développer l'application de manière standalone avec les ports exposés :

1. **Construire et démarrer les conteneurs**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```

2. **Accéder à l'application**
   - Application Django : http://localhost:8000
   - Base de données PostgreSQL : localhost:5432

3. **Exécuter les migrations**
   ```bash
   docker-compose exec dls3-web python manage.py migrate
   ```

4. **Créer un superutilisateur**
   ```bash
   docker-compose exec dls3-web python manage.py createsuperuser
   ```

### Intégration dans une application existante

Pour intégrer DLS3 dans votre application existante avec Nginx, consultez le fichier **[INTEGRATION.md](./INTEGRATION.md)** qui contient :
- Instructions d'intégration dans votre docker-compose.yml
- Configuration Nginx (fichier `nginx.conf` fourni)
- Configuration réseau Docker
- Exemples de liens depuis votre application

### Commandes utiles

- **Arrêter les conteneurs**
  ```bash
  docker-compose down
  ```

- **Voir les logs**
  ```bash
  docker-compose logs -f dls3-web
  ```

- **Exécuter des commandes Django**
  ```bash
  docker-compose exec dls3-web python manage.py <commande>
  ```

- **Accéder au shell Django**
  ```bash
  docker-compose exec dls3-web python manage.py shell
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
├── config/                  # Configuration Django
├── manage.py                # Script de gestion Django
├── requirements.txt         # Dépendances Python
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration Docker (pour intégration)
├── docker-compose.dev.yml  # Surcharge pour développement standalone
├── nginx.conf              # Configuration Nginx pour intégration
├── .env.example            # Variables d'environnement d'exemple
├── INTEGRATION.md          # Guide d'intégration détaillé
└── README.md               # Ce fichier
```
