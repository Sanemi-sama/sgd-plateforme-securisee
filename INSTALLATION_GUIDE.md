# 🚀 Guide d'Installation de la Plateforme SGD

Ce guide explique les étapes nécessaires pour déployer la stack complète (Django + Wazuh + TheHive) sur une nouvelle machine après avoir cloné le dépôt.

---

## 📋 Prérequis Système

- **OS** : Linux (Ubuntu/Debian recommandé)
- **RAM** : 8 Go minimum (16 Go recommandés)
- **CPU** : 4 cœurs minimum
- **Docker** & **Docker Compose** installés

---

## 🛠️ Étape 1 : Configuration de l'Hôte (Indispensable)

Wazuh Indexer nécessite une limite de mémoire virtuelle élevée pour fonctionner.
Exécutez cette commande sur votre machine hôte :

```bash
sudo sysctl -w vm.max_map_count=262144
# Pour rendre ce changement permanent après redémarrage :
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

---

## 🔑 Étape 2 : Variables d'Environnement

Le projet utilise des variables d'environnement pour sécuriser les mots de passe.

1. Copiez le fichier d'exemple :
   ```bash
   cp docker/.env.example .env
   ```
2. Modifiez le fichier `.env` pour définir vos propres mots de passe (utilisez des mots de passe complexes pour Wazuh).

---

## 📜 Étape 3 : Déploiement Automatisé

Utilisez le script `setup.sh` qui automatise la majeure partie de la configuration :

```bash
chmod +x setup.sh
./setup.sh --install
```

**Ce que fait ce script :**
1. Vérifie la configuration système.
2. Génère les certificats SSL nécessaires à la communication entre les composants Wazuh.
3. Lance tous les conteneurs Docker.
4. Effectue les migrations de la base de données Django.
5. Crée un compte administrateur Django par défaut.

---

## 🔐 Étape 4 : Initialisation de la Sécurité (Si nécessaire)

Si après l'installation, le Dashboard Wazuh affiche une erreur de connexion, exécutez manuellement l'initialisation de l'index de sécurité :

```bash
docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk sgd_wazuh_indexer \
  /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh \
  -cd /usr/share/wazuh-indexer/config/opensearch-security/ \
  -icl -nhnv \
  -cacert /usr/share/wazuh-indexer/config/certs/root-ca.pem \
  -cert /usr/share/wazuh-indexer/config/certs/admin.pem \
  -key /usr/share/wazuh-indexer/config/certs/admin-key.pem \
  -h localhost
```

---

## 🐝 Étape 5 : Configuration Post-Installation TheHive

1. Connectez-vous à TheHive : `http://localhost:9000`
   - **Login** : `admin@thehive.local`
   - **Pass** : `secret`
2. Créez votre organisation et un utilisateur.
3. Générez une **Clé API** pour cet utilisateur.
4. Copiez cette clé dans votre fichier `.env` sous la variable `THEHIVE_API_KEY`.
5. Redémarrez le conteneur Django : `docker-compose restart django`.

---

## 🌐 Accès aux Services

- **Application SGD** : [http://localhost:8000](http://localhost:8000)
- **Wazuh Dashboard** : [http://localhost:5601](http://localhost:5601)
- **TheHive** : [http://localhost:9000](http://localhost:9000)

---

## 📂 Structure des Fichiers Importants

- `docker/docker-compose.yml` : Orchestration des services.
- `apps/dashboard/` : Code Django gérant l'intégration avec Wazuh et TheHive.
- `docker/wazuh/config/` : Fichiers de configuration spécifiques à Wazuh.
