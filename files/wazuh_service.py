"""
Service d'intégration Wazuh 4.14.4
API Manager  : https://wazuh-manager:55000  (JWT)
API Indexer  : https://wazuh-indexer:9200   (Basic Auth - pour les alertes)
"""
import requests
import urllib3
from django.conf import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WazuhService:

    def __init__(self):
        self.manager_url  = getattr(settings, 'WAZUH_API_URL',           'https://wazuh-manager:55000')
        self.indexer_url  = getattr(settings, 'WAZUH_INDEXER_URL',       'https://wazuh-indexer:9200')
        self.username     = getattr(settings, 'WAZUH_API_USER',          'wazuh-wui')
        self.password     = getattr(settings, 'WAZUH_API_PASSWORD',      'changeme')
        self.indexer_user = getattr(settings, 'WAZUH_INDEXER_USER',      'admin')
        self.indexer_pass = getattr(settings, 'WAZUH_INDEXER_PASSWORD',  'changeme')
        self._token       = None

    # ══════════════════════════════════════════
    #  AUTH — Manager API (JWT)
    # ══════════════════════════════════════════
    def _get_token(self):
        try:
            resp = requests.post(
                f"{self.manager_url}/security/user/authenticate",
                auth=(self.username, self.password),
                verify=False, timeout=8,
            )
            if resp.status_code == 200:
                return resp.json()['data']['token']
        except Exception as e:
            print(f"[Wazuh] Auth error: {e}")
        return None

    def _manager_headers(self):
        if not self._token:
            self._token = self._get_token()
        return {'Authorization': f'Bearer {self._token}', 'Content-Type': 'application/json'}

    # ══════════════════════════════════════════
    #  MANAGER API — agents, statut
    # ══════════════════════════════════════════
    def _manager_get(self, endpoint, params=None):
        try:
            resp = requests.get(
                f"{self.manager_url}{endpoint}",
                headers=self._manager_headers(),
                params=params, verify=False, timeout=8,
            )
            if resp.status_code == 401:
                self._token = self._get_token()
                resp = requests.get(
                    f"{self.manager_url}{endpoint}",
                    headers=self._manager_headers(),
                    params=params, verify=False, timeout=8,
                )
            if resp.status_code == 200:
                return resp.json().get('data', {})
        except Exception as e:
            print(f"[Wazuh] Manager GET {endpoint}: {e}")
        return None

    def get_agents(self):
        """Liste des agents connectés."""
        data = self._manager_get('/agents', {'limit': 100, 'status': 'active'})
        return data.get('affected_items', []) if data else []

    def get_agents_summary(self):
        """Résumé des statuts agents."""
        data = self._manager_get('/agents/summary/status')
        if data:
            conn = data.get('connection', {})
            return {
                'active':           conn.get('active', 0),
                'disconnected':     conn.get('disconnected', 0),
                'never_connected':  conn.get('never_connected', 0),
                'total':            conn.get('total', 0),
            }
        return {'active': 0, 'disconnected': 0, 'never_connected': 0, 'total': 0}

    def is_available(self):
        """Vérifie si le manager Wazuh répond."""
        try:
            return self._get_token() is not None
        except Exception:
            return False

    # ══════════════════════════════════════════
    #  INDEXER API — alertes (OpenSearch)
    #  En 4.14.x les alertes sont dans l'index
    #  wazuh-alerts-4.x-YYYY.MM.DD
    # ══════════════════════════════════════════
    def _indexer_search(self, query, size=20):
        try:
            resp = requests.post(
                f"{self.indexer_url}/wazuh-alerts-*/_search",
                auth=(self.indexer_user, self.indexer_pass),
                json=query, verify=False, timeout=10,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[Wazuh] Indexer search error: {e}")
        return None

    def get_alerts(self, limit=20, min_level=None, offset=0):
        """
        Récupère les dernières alertes depuis l'indexeur OpenSearch.
        min_level : niveau minimum Wazuh (1-15)
        """
        must = []
        if min_level:
            must.append({'range': {'rule.level': {'gte': int(min_level)}}})

        query = {
            'from': offset,
            'size': limit,
            'sort': [{'timestamp': {'order': 'desc'}}],
            'query': {'bool': {'must': must}} if must else {'match_all': {}},
            '_source': [
                'timestamp', 'rule.level', 'rule.description',
                'rule.groups', 'rule.id', 'agent.name', 'agent.ip',
                'location', 'full_log',
            ],
        }
        result = self._indexer_search(query, size=limit)
        if result:
            hits = result.get('hits', {}).get('hits', [])
            return [h['_source'] for h in hits]
        return []

    def get_alerts_summary(self):
        """Nombre d'alertes par niveau de sévérité."""
        def _count(min_l, max_l):
            q = {
                'size': 0,
                'query': {'range': {'rule.level': {'gte': min_l, 'lte': max_l}}},
            }
            r = self._indexer_search(q)
            return r['hits']['total']['value'] if r else 0

        try:
            return {
                'total':    _count(1, 15),
                'critical': _count(12, 15),
                'high':     _count(8, 11),
                'medium':   _count(4, 7),
                'low':      _count(1, 3),
            }
        except Exception as e:
            print(f"[Wazuh] Summary error: {e}")
            return {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

    # ══════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════
    @staticmethod
    def level_to_severity(level):
        """Convertit le niveau Wazuh (1-15) en label + classe CSS."""
        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 0
        if level >= 12:
            return 'Critique', 'badge-danger'
        elif level >= 8:
            return 'Haute', 'badge-warning'
        elif level >= 4:
            return 'Moyenne', 'badge-info'
        else:
            return 'Basse', 'badge-secondary'
