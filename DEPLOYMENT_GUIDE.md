# Guide de Déploiement SGD - Plateforme Sécurisée

Ce guide détaille les étapes pour déployer la stack complète sur Windows.

## 1. Prérequis
- Docker Desktop installé et fonctionnel.
- OpenSSL installé (disponible via Git Bash ou installation directe).

## 2. Préparation des fichiers
```powershell
# Cloner le dépôt
git clone <url-du-repo>
cd sgd-plateforme-securisee

# Créer le fichier d'environnement
copy docker\.env.example docker\.env
```

## 3. Génération des Certificats SSL (Wazuh)
Exécutez ces commandes pour créer les certificats nécessaires à la sécurité de l'Indexer.
*Important : Respectez l'ordre des DN pour la compatibilité avec la configuration.*

```powershell
# Créer le dossier des certificats
mkdir -p docker/wazuh/config/certs

# 1. Root CA
openssl genrsa -out docker/wazuh/config/certs/root-ca-key.pem 2048
openssl req -new -x509 -sha256 -key docker/wazuh/config/certs/root-ca-key.pem -out docker/wazuh/config/certs/root-ca.pem -days 730 -subj "/C=BJ/L=Cotonou/O=SGD/OU=SGD/CN=root-ca"

# 2. Wazuh Indexer
openssl genrsa -out docker/wazuh/config/certs/wazuh-indexer-key.pem 2048
openssl req -new -key docker/wazuh/config/certs/wazuh-indexer-key.pem -out docker/wazuh/config/certs/wazuh-indexer.csr -subj "/C=BJ/O=SGD/CN=wazuh-indexer"
openssl x509 -req -in docker/wazuh/config/certs/wazuh-indexer.csr -CA docker/wazuh/config/certs/root-ca.pem -CAkey docker/wazuh/config/certs/root-ca-key.pem -CAcreateserial -out docker/wazuh/config/certs/wazuh-indexer.pem -days 730 -sha256

# 3. Admin Certificate (Celui qui a posé problème précédemment)
openssl genrsa -out docker/wazuh/config/certs/admin-key.pem 2048
openssl req -new -key docker/wazuh/config/certs/admin-key.pem -out docker/wazuh/config/certs/admin.csr -subj "/C=BJ/O=SGD/OU=Wazuh/CN=admin"
openssl x509 -req -in docker/wazuh/config/certs/admin.csr -CA docker/wazuh/config/certs/root-ca.pem -CAkey docker/wazuh/config/certs/root-ca-key.pem -CAcreateserial -out docker/wazuh/config/certs/admin.pem -days 730 -sha256

# 4. Wazuh Manager & Dashboard (Certificats simplifiés)
# Manager
openssl genrsa -out docker/wazuh/config/certs/wazuh-manager-key.pem 2048
openssl req -new -key docker/wazuh/config/certs/wazuh-manager-key.pem -out docker/wazuh/config/certs/wazuh-manager.csr -subj "/C=BJ/O=SGD/CN=wazuh-manager"
openssl x509 -req -in docker/wazuh/config/certs/wazuh-manager.csr -CA docker/wazuh/config/certs/root-ca.pem -CAkey docker/wazuh/config/certs/root-ca-key.pem -CAcreateserial -out docker/wazuh/config/certs/wazuh-manager.pem -days 730 -sha256
# Dashboard
openssl genrsa -out docker/wazuh/config/certs/wazuh-dashboard-key.pem 2048
openssl req -new -key docker/wazuh/config/certs/wazuh-dashboard-key.pem -out docker/wazuh/config/certs/wazuh-dashboard.csr -subj "/C=BJ/O=SGD/CN=wazuh-dashboard"
openssl x509 -req -in docker/wazuh/config/certs/wazuh-dashboard.csr -CA docker/wazuh/config/certs/root-ca.pem -CAkey docker/wazuh/config/certs/root-ca-key.pem -CAcreateserial -out docker/wazuh/config/certs/wazuh-dashboard.pem -days 730 -sha256

# Nettoyage
rm docker/wazuh/config/certs/*.csr
rm docker/wazuh/config/certs/*.srl
```

## 4. Lancement de la Stack
```powershell
# Build et lancement
docker compose -f docker/docker-compose.yml up -d --build
```

## 5. Initialisation de la Sécurité
Attendez que l'indexer soit `healthy` (environ 2-3 min), puis lancez :
```powershell
docker exec -e OPENSEARCH_JAVA_HOME=/usr/share/wazuh-indexer/jdk sgd_wazuh_indexer /usr/share/wazuh-indexer/plugins/opensearch-security/tools/securityadmin.sh -cd /usr/share/wazuh-indexer/config/opensearch-security/ -icl -nhnv -cacert /usr/share/wazuh-indexer/config/certs/root-ca.pem -cert /usr/share/wazuh-indexer/config/certs/admin.pem -key /usr/share/wazuh-indexer/config/certs/admin-key.pem -h localhost
```

## 6. Finalisation
Redémarrez le manager pour injecter les templates d'alertes :
```powershell
docker restart sgd_wazuh_manager
```

## 7. Accès
- **SGD App** : http://localhost
- **Wazuh Dashboard** : http://localhost:5601
- **TheHive** : http://localhost:9000
