# Intégration de DLS3 dans une application existante

Ce guide explique comment intégrer l'application Django DLS3 dans votre application existante avec Docker Compose et Nginx.

## Prérequis

- Docker et Docker Compose installés
- Une application avec un serveur Nginx configuré
- Les deux applications doivent partager le même réseau Docker

## Étape 1 : Intégration dans votre docker-compose.yml

Dans votre fichier `docker-compose.yml` existant, ajoutez les services DLS3 :

```yaml
services:
  # Vos services existants...

  dls3-db:
    image: postgres:16-alpine
    container_name: dls3-db
    volumes:
      - dls3_postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=dls3_db
      - POSTGRES_USER=dls3_user
      - POSTGRES_PASSWORD=dls3_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dls3_user -d dls3_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - votre-reseau-existant  # Utilisez votre réseau existant

  dls3-web:
    build: ./path/to/dls3  # Chemin vers le dossier dls3
    container_name: dls3-web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./path/to/dls3:/app
    expose:
      - "8000"
    environment:
      - DEBUG=1
      - DB_HOST=dls3-db
      - DB_NAME=dls3_db
      - DB_USER=dls3_user
      - DB_PASSWORD=dls3_password
      - DB_PORT=5432
    depends_on:
      dls3-db:
        condition: service_healthy
    networks:
      - votre-reseau-existant  # Utilisez votre réseau existant

volumes:
  dls3_postgres_data:
  # Vos volumes existants...
```

## Étape 2 : Configuration Nginx

### Option A : Intégration dans votre configuration Nginx existante

Ajoutez cette configuration dans votre fichier de configuration Nginx existant :

```nginx
# Upstream pour DLS3
upstream dls3_app {
    server dls3-web:8000;
}

# Dans votre server block existant
server {
    # Votre configuration existante...

    # Redirection vers DLS3 sur un sous-chemin
    location /dls3/ {
        rewrite ^/dls3(.*)$ $1 break;
        proxy_pass http://dls3_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Option B : Configuration sur un sous-domaine

```nginx
upstream dls3_app {
    server dls3-web:8000;
}

server {
    listen 80;
    server_name dls3.votredomaine.com;

    location / {
        proxy_pass http://dls3_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Fichiers statiques
    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

## Étape 3 : Lien depuis votre application existante

Dans votre application frontend, ajoutez un lien vers DLS3 :

### Option A : Sous-chemin
```html
<a href="/dls3/" target="_blank">Accéder à DLS3</a>
```

### Option B : Sous-domaine
```html
<a href="http://dls3.votredomaine.com" target="_blank">Accéder à DLS3</a>
```

## Étape 4 : Configuration Django

Si vous utilisez un sous-chemin, modifiez le fichier `config/settings.py` :

```python
# Ajouter à settings.py
FORCE_SCRIPT_NAME = '/dls3'
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Étape 5 : Démarrage

```bash
# Construire et démarrer tous les services
docker-compose up --build -d

# Exécuter les migrations DLS3
docker-compose exec dls3-web python manage.py migrate

# Créer un superutilisateur (optionnel)
docker-compose exec dls3-web python manage.py createsuperuser
```

## Exemple de configuration réseau partagé

Si votre docker-compose existant utilise un réseau nommé `app-network` :

```yaml
networks:
  app-network:
    name: app-network
    driver: bridge
```

Assurez-vous que les services DLS3 utilisent le même réseau :

```yaml
services:
  dls3-web:
    networks:
      - app-network
  dls3-db:
    networks:
      - app-network
```

## Vérification

1. Vérifiez que tous les conteneurs sont démarrés :
   ```bash
   docker-compose ps
   ```

2. Vérifiez que Nginx peut atteindre DLS3 :
   ```bash
   docker-compose exec nginx curl http://dls3-web:8000
   ```

3. Testez l'accès via votre navigateur

## Dépannage

### Le service DLS3 n'est pas accessible
- Vérifiez que les conteneurs sont sur le même réseau
- Vérifiez les logs : `docker-compose logs dls3-web`

### Erreur 502 Bad Gateway
- Vérifiez que le conteneur dls3-web est démarré
- Vérifiez la configuration upstream dans Nginx

### Problèmes de base de données
- Vérifiez que dls3-db est healthy : `docker-compose ps dls3-db`
- Vérifiez les logs : `docker-compose logs dls3-db`
