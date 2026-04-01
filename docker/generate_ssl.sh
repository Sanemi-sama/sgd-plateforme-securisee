#!/bin/bash
# ─────────────────────────────────────────────────────────
#  Génère un certificat auto-signé pour le développement
#  À NE PAS utiliser en production (utilise Let's Encrypt)
# ─────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$SCRIPT_DIR/ssl"

mkdir -p "$SSL_DIR"

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "$SSL_DIR/key.pem" \
  -out "$SSL_DIR/cert.pem" \
  -subj "/C=BJ/ST=Atlantique/L=Cotonou/O=SGD/CN=localhost"

echo "✅ Certificat auto-signé généré dans $SSL_DIR"
echo "   cert.pem  → certificat"
echo "   key.pem   → clé privée"
