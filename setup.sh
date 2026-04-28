#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  SGD — Script d'installation automatique
#  Compatible : Linux (Debian/Ubuntu/Parrot/Kali) & macOS
#  Usage      : bash setup.sh
#               bash setup.sh --clean (nettoie puis réinstalle)
# ══════════════════════════════════════════════════════════════

set -e

# ── Arguments ──────────────────────────────────────────────────
CLEAN_MODE=false
if [[ "$1" == "--clean" ]]; then
    CLEAN_MODE=true
fi

# ── Couleurs ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
step()    { echo -e "\n${BOLD}${CYAN}══ $1 ══${NC}"; }

# ── Détection du chemin du projet ────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BOLD}"
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║   SGD — Plateforme Sécurisée de Gestion   ║"
echo "  ║         Script d'installation v1.1         ║"
echo "  ╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# ══════════════════════════════════════════════════════════════
# ÉTAPE 0 — Vérifications prérequis
# ══════════════════════════════════════════════════════════════
step "Vérification des prérequis"

if ! command -v docker &>/dev/null; then
    error "Docker n'est pas installé. Installe-le depuis https://docs.docker.com/get-docker/"
fi
success "Docker $(docker --version | cut -d' ' -f3 | tr -d ',')"

if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
else
    error "Docker Compose n'est pas installé."
fi
success "Docker Compose disponible ($COMPOSE_CMD)"

if ! command -v openssl &>/dev/null; then
    error "OpenSSL n'est pas installé. Lance : sudo apt install openssl"
fi
success "OpenSSL $(openssl version | cut -d' ' -f2)"

# vm.max_map_count (requis par Wazuh Indexer)
CURRENT_MAP=$(sysctl -n vm.max_map_count 2>/dev/null || echo 0)
if [ "$CURRENT_MAP" -lt 262144 ]; then
    warn "vm.max_map_count=$CURRENT_MAP — configuration pour Wazuh Indexer..."
    sudo sysctl -w vm.max_map_count=262144
    echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf > /dev/null
    success "vm.max_map_count=262144 configuré"
else
    success "vm.max_map_count=$CURRENT_MAP (OK)"
fi

# ══════════════════════════════════════════════════════════════
# ÉTAPE 0b — Nettoyage si mode --clean
# ══════════════════════════════════════════════════════════════
if [ "$CLEAN_MODE" = true ]; then
    step "Nettoyage des anciennes données"

    warn "Arrêt et suppression des conteneurs..."
    $COMPOSE_CMD -f docker/docker-compose.yml down -v 2>/dev/null || true
    docker volume rm sgd-plateforme-securisee_wazuh_indexer_data 2>/dev/null || true
    docker volume rm sgd-plateforme-securisee_postgres_data 2>/dev/null || true
    docker volume rm sgd-plateforme-securisee_cortex_data 2>/dev/null || true
    docker volume rm sgd-plateforme-securisee_elasticsearch_data 2>/dev/null || true
    docker volume rm sgd-plateforme-securisee_thehive_data 2>/dev/null || true
    docker volume rm sgd-plateforme-securisee_thehive_index 2>/dev/null || true

    warn "Suppression des conteneurs orphelins..."
    docker container prune -f 2>/dev/null || true

    success "Nettoyage terminé"
fi

# ══════════════════════════════════════════════════════════════
# ÉTAPE 1 — Fichier .env
# ══════════════════════════════════════════════════════════════
step "Configuration du fichier .env"

if [ ! -f docker/.env ]; then
    if [ -f docker/.env.example ]; then
        cp docker/.env.example docker/.env
        success "Fichier docker/.env créé depuis .env.example"
        warn "Pense à personnaliser docker/.env avec tes propres valeurs !"
    else
        error "Fichier docker/.env.example introuvable !"
    fi
else
    success "Fichier docker/.env déjà existant"
fi

# ══════════════════════════════════════════════════════════════
# ÉTAPE 2 — Certificats SSL Wazuh
# ══════════════════════════════════════════════════════════════
step "Génération des certificats SSL Wazuh"

CERTS_DIR="docker/wazuh/config/certs"
mkdir -p "$CERTS_DIR"

if [ -f "$CERTS_DIR/root-ca.pem" ] && [ -f "$CERTS_DIR/wazuh-indexer.pem" ] && \
   [ -f "$CERTS_DIR/wazuh-manager.pem" ] && [ -f "$CERTS_DIR/wazuh-dashboard.pem" ]; then
    success "Certificats déjà présents — skipping"
else
    info "Génération des certificats avec OpenSSL..."

    # Root CA
    openssl genrsa -out "$CERTS_DIR/root-ca-key.pem" 2048 2>/dev/null
    openssl req -new -x509 -sha256 \
        -key "$CERTS_DIR/root-ca-key.pem" \
        -out "$CERTS_DIR/root-ca.pem" -days 730 \
        -subj "/C=BJ/L=Cotonou/O=SGD/OU=SGD/CN=root-ca" 2>/dev/null
    cp "$CERTS_DIR/root-ca.pem" "$CERTS_DIR/root-ca-manager.pem"

    # Wazuh Indexer
    openssl genrsa -out "$CERTS_DIR/wazuh-indexer-key.pem" 2048 2>/dev/null
    openssl req -new -key "$CERTS_DIR/wazuh-indexer-key.pem" \
        -out "$CERTS_DIR/wazuh-indexer.csr" \
        -subj "/C=BJ/O=SGD/CN=wazuh-indexer" 2>/dev/null
    openssl x509 -req -in "$CERTS_DIR/wazuh-indexer.csr" \
        -CA "$CERTS_DIR/root-ca.pem" -CAkey "$CERTS_DIR/root-ca-key.pem" \
        -CAcreateserial -out "$CERTS_DIR/wazuh-indexer.pem" -days 730 -sha256 2>/dev/null

    # Wazuh Manager
    openssl genrsa -out "$CERTS_DIR/wazuh-manager-key.pem" 2048 2>/dev/null
    openssl req -new -key "$CERTS_DIR/wazuh-manager-key.pem" \
        -out "$CERTS_DIR/wazuh-manager.csr" \
        -subj "/C=BJ/O=SGD/CN=wazuh-manager" 2>/dev/null
    openssl x509 -req -in "$CERTS_DIR/wazuh-manager.csr" \
        -CA "$CERTS_DIR/root-ca.pem" -CAkey "$CERTS_DIR/root-ca-key.pem" \
        -CAcreateserial -out "$CERTS_DIR/wazuh-manager.pem" -days 730 -sha256 2>/dev/null

    # Wazuh Dashboard
    openssl genrsa -out "$CERTS_DIR/wazuh-dashboard-key.pem" 2048 2>/dev/null
    openssl req -new -key "$CERTS_DIR/wazuh-dashboard-key.pem" \
        -out "$CERTS_DIR/wazuh-dashboard.csr" \
        -subj "/C=BJ/O=SGD/CN=wazuh-dashboard" 2>/dev/null
    openssl x509 -req -in "$CERTS_DIR/wazuh-dashboard.csr" \
        -CA "$CERTS_DIR/root-ca.pem" -CAkey "$CERTS_DIR/root-ca-key.pem" \
        -CAcreateserial -out "$CERTS_DIR/wazuh-dashboard.pem" -days 730 -sha256 2>/dev/null

    # Admin (pour securityadmin.sh)
    openssl genrsa -out "$CERTS_DIR/admin-key.pem" 2048 2>/dev/null
    openssl req -new -key "$CERTS_DIR/admin-key.pem" \
        -out "$CERTS_DIR/admin.csr" \
        -subj "/C=BJ/O=SGD/OU=Wazuh/CN=admin" 2>/dev/null
    openssl x509 -req -in "$CERTS_DIR/admin.csr" \
        -CA "$CERTS_DIR/root-ca.pem" -CAkey "$CERTS_DIR/root-ca-key.pem" \
        -CAcreateserial -out "$CERTS_DIR/admin.pem" -days 730 -sha256 2>/dev/null

    # Nettoyage fichiers temporaires
    rm -f "$CERTS_DIR"/*.csr "$CERTS_DIR"/*.srl

    success "Certificats SSL générés dans $CERTS_DIR"
fi

# ══════════════════════════════════════════════════════════════
# ÉTAPE 3 — Démarrage des conteneurs
# ══════════════════════════════════════════════════════════════
step "Démarrage des conteneurs Docker"

info "Build et démarrage (peut prendre 5-15 min au premier lancement)..."
$COMPOSE_CMD -f docker/docker-compose.yml --env-file docker/.env up -d --build

success "Conteneurs démarrés"

# ══════════════════════════════════════════════════════════════
# ÉTAPE 4 — Attente PostgreSQL + Django
# ══════════════════════════════════════════════════════════════
step "Attente du démarrage de Django"

info "Attente que Gunicorn soit prêt..."
MAX_WAIT=120
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if $COMPOSE_CMD -f docker/docker-compose.yml logs django 2>/dev/null | grep -q "Booting worker"; then
        success "Django est prêt !"
        break
    fi
    sleep 5
    WAITED=$((WAITED + 5))
    echo -n "."
done
echo ""
if [ $WAITED -ge $MAX_WAIT ]; then
    warn "Django met du temps — vérifier avec : $COMPOSE_CMD -f docker/docker-compose.yml logs django"
fi

# ══════════════════════════════════════════════════════════════
# ÉTAPE 5 — Initialisation de la sécurité Wazuh Indexer
# ══════════════════════════════════════════════════════════════
step "Initialisation sécurité Wazuh Indexer"

info "Attente que l'indexer Wazuh soit healthy (peut prendre 3-7 min)..."
MAX_WAIT=420
WAITED=0
INDEXER_READY=false

while [ $WAITED -lt $MAX_WAIT ]; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' sgd_wazuh_indexer 2>/dev/null || echo "unknown")
    if [ "$STATUS" = "healthy" ]; then
        INDEXER_READY=true
        break
    fi
    sleep 10
    WAITED=$((WAITED + 10))
    echo -n ". (${WAITED}s - status: $STATUS)"
done
echo ""

if [ "$INDEXER_READY" = false ]; then
    warn "L'indexer n'est pas encore healthy après ${MAX_WAIT}s."
    warn "Lance manuellement après que l'indexer soit prêt :"
    warn "  docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk sgd_wazuh_indexer \\"
    warn "    /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \\"
    warn "    -cd /usr/share/wazuh-indexer/config/opensearch-security/ -icl -nhnv \\"
    warn "    -cacert /usr/share/wazuh-indexer/config/certs/root-ca.pem \\"
    warn "    -cert /usr/share/wazuh-indexer/config/certs/admin.pem \\"
    warn "    -key /usr/share/wazuh-indexer/config/certs/admin-key.pem -h localhost"
else
    success "Indexer healthy après ${WAITED}s !"

    # Attente supplémentaire pour stabilisation
    info "Stabilisation de l'indexer (30s)..."
    sleep 30

    info "Initialisation de la sécurité OpenSearch..."
    docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk sgd_wazuh_indexer \
        /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \
        -cd /usr/share/wazuh-indexer/config/opensearch-security/ \
        -icl -nhnv \
        -cacert /usr/share/wazuh-indexer/config/certs/root-ca.pem \
        -cert /usr/share/wazuh-indexer/config/certs/admin.pem \
        -key /usr/share/wazuh-indexer/config/certs/admin-key.pem \
        -h localhost 2>/dev/null && success "Sécurité OpenSearch initialisée !" || \
        warn "Sécurité déjà initialisée — pas bloquant"
fi

# ══════════════════════════════════════════════════════════════
# ÉTAPE 6 — Données de démonstration Django
# ══════════════════════════════════════════════════════════════
step "Initialisation des données Django"

info "Chargement des données de démonstration..."
$COMPOSE_CMD -f docker/docker-compose.yml --env-file docker/.env \
    exec -T django python manage.py init_data && \
    success "Données de démonstration chargées" || \
    warn "Données déjà existantes — pas bloquant"

# ══════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ══════════════════════════════════════════════════════════════
echo ""
echo -e "${BOLD}${GREEN}"
echo "  ╔═══════════════════════════════════════════════════╗"
echo "  ║           ✅  Installation terminée !              ║"
echo "  ╠═══════════════════════════════════════════════════╣"
echo "  ║                                                   ║"
echo "  ║  🌐 Application SGD   →  http://localhost:8000    ║"
echo "  ║  🔐 Wazuh Dashboard   →  http://localhost:5601    ║"
echo "  ║  🐝 TheHive           →  http://localhost:9000    ║"
echo "  ║  📋 OpenProject       →  http://localhost:8081    ║"
echo "  ║                                                   ║"
echo "  ║  Identifiants SGD :  admin / Admin1234!           ║"
echo "  ║  Identifiants Wazuh: admin / admin                ║"
echo "  ║                                                   ║"
echo "  ╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

warn "Le dashboard Wazuh peut prendre 2-3 min supplémentaires à être accessible."
info "Pour voir les logs : $COMPOSE_CMD -f docker/docker-compose.yml logs -f"
