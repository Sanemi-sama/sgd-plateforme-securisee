# 🐳 Docker Setup — SGD (Plateforme Sécurisée de Gestion des Dossiers)

## 📁 Structure des fichiers

```
projet/
├── docker/
│   ├── Dockerfile              ← Image Django (multi-stage)
│   ├── docker-compose.yml      ← Stack complète
│   ├── entrypoint.sh           ← Script démarrage Django
│   ├── .env.example            ← Template des variables d'environnement
│   ├── generate_ssl.sh         ← Génère le certificat auto-signé (dev)
│   ├── nginx/
│   │   └── conf.d/
│   │       └── django.conf     ← Config Nginx + HTTPS
│   ├── wazuh/
│   │   └── config/
│   │       └── ossec.conf      ← Config Wazuh (à adapter)
│   └── thehive/
│       └── config/
│           └── application.conf← Config TheHive (à adapter)
└── Makefile                    ← Commandes rapides
```

## 🚀 Premier démarrage (Windows)

### Prérequis
- [Docker Desktop pour Windows](https://www.docker.com/products/docker-desktop/) installé et lancé
- [Git](https://git-scm.com/) installé
- WSL2 activé (recommandé pour de meilleures performances)
- OpenSSL installé (fourni avec Git pour Windows)

### Étapes

```bash
# 1. Clone le projet
git clone https://github.com/ton-user/ton-repo.git
cd ton-repo

# 2. Copie le fichier .env et édite-le avec tes vraies valeurs
cp docker/.env.example docker/.env
# Ouvre docker/.env et change tous les "changeme" !

# 3. Génère le certificat SSL auto-signé (pour dev local)
bash docker/generate_ssl.sh

# 4. Build et démarre tout
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d --build

# OU avec le Makefile (si make est installé) :
make setup
```

## 🌐 Accès aux services

| Service | URL | Identifiants par défaut |
|---------|-----|------------------------|
| **Django** | https://localhost | Défini dans `.env` |
| **Wazuh Dashboard** | http://localhost:5601 | admin / (défini dans .env) |
| **TheHive** | http://localhost:9000 | admin@thehive.local / secret |

## 🔧 Commandes utiles

```bash
# Voir les logs en temps réel
docker compose -f docker/docker-compose.yml logs -f django

# Ouvrir un shell Django
docker compose -f docker/docker-compose.yml exec django python manage.py shell

# Lancer les migrations manuellement
docker compose -f docker/docker-compose.yml exec django python manage.py migrate

# Arrêter tous les services
docker compose -f docker/docker-compose.yml down
```

Avec le Makefile :
```bash
make logs-django
make shell
make migrate
make down
```

## ⚠️ Points importants

1. **Ne jamais commiter `docker/.env`** — ajoute-le dans `.gitignore`
2. Le certificat SSL auto-signé va afficher un avertissement dans le navigateur → clique sur "Avancer quand même" en dev
3. **Wazuh et TheHive sont gourmands en RAM** : prévois au minimum **8 Go de RAM** sur ta machine
4. En production, remplace le certificat auto-signé par Let's Encrypt

## 📌 .gitignore à compléter

```
docker/.env
docker/ssl/
logs/
*.pyc
__pycache__/
.DS_Store
```
