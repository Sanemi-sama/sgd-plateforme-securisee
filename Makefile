# ══════════════════════════════════════════════
#  Makefile — Commandes rapides pour le projet
#  Usage : make <commande>
# ══════════════════════════════════════════════

COMPOSE = docker compose -f docker/docker-compose.yml --env-file docker/.env

.PHONY: help build up down restart logs shell migrate static createsuperuser clean

help:  ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup initial ─────────────────────────────
setup: ## Premier démarrage complet (SSL + build + up)
	@echo "🔐 Génération du certificat SSL..."
	@bash docker/generate_ssl.sh
	@echo "📋 Copie du fichier .env..."
	@cp -n docker/.env.example docker/.env || true
	@echo "⚠️  Pense à éditer docker/.env avec tes vraies valeurs !"
	@$(MAKE) build
	@$(MAKE) up

# ── Cycle de vie ──────────────────────────────
build: ## Build les images Docker
	$(COMPOSE) build --no-cache

up: ## Démarre tous les services
	$(COMPOSE) up -d

down: ## Arrête tous les services
	$(COMPOSE) down

restart: ## Redémarre le service Django uniquement
	$(COMPOSE) restart django

# ── Django ────────────────────────────────────
shell: ## Ouvre un shell dans le conteneur Django
	$(COMPOSE) exec django python manage.py shell

bash: ## Ouvre un bash dans le conteneur Django
	$(COMPOSE) exec django bash

migrate: ## Lance les migrations
	$(COMPOSE) exec django python manage.py migrate

static: ## Collecte les fichiers statiques
	$(COMPOSE) exec django python manage.py collectstatic --noinput

createsuperuser: ## Crée un superuser manuellement
	$(COMPOSE) exec django python manage.py createsuperuser

# ── Logs ──────────────────────────────────────
logs: ## Affiche les logs de tous les services
	$(COMPOSE) logs -f

logs-django: ## Logs Django uniquement
	$(COMPOSE) logs -f django

logs-wazuh: ## Logs Wazuh uniquement
	$(COMPOSE) logs -f wazuh-manager

logs-thehive: ## Logs TheHive uniquement
	$(COMPOSE) logs -f thehive

# ── Nettoyage ─────────────────────────────────
clean: ## Supprime conteneurs, volumes et images du projet
	$(COMPOSE) down -v --rmi local
	@echo "🧹 Nettoyage terminé"
