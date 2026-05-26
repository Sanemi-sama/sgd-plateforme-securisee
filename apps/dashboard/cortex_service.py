"""
Service d'intégration Cortex 3.x
Vérifie la disponibilité du service.
"""
import requests
from django.conf import settings


class CortexService:

    def __init__(self):
        self.base_url = getattr(settings, 'CORTEX_URL', 'http://cortex:9001')
        self.api_key  = getattr(settings, 'CORTEX_API_KEY', '')

    def is_available(self):
        """Vérifie si le service Cortex répond."""
        try:
            # On teste l'API de statut ou simplement la racine
            resp = requests.get(f"{self.base_url}/status", timeout=2)
            return resp.status_code == 200
        except Exception:
            try:
                # Fallback sur la racine si /status n'est pas dispo sans auth
                resp = requests.get(self.base_url, timeout=2)
                return resp.status_code == 200
            except Exception:
                return False
