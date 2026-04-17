"""
Service d'intégration TheHive 5.x
Crée des alertes/cas depuis les alertes Wazuh.
"""
import requests
from django.conf import settings


class TheHiveService:

    def __init__(self):
        self.base_url = getattr(settings, 'THEHIVE_URL',     'http://thehive:9000')
        self.api_key  = getattr(settings, 'THEHIVE_API_KEY', '')

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type':  'application/json',
        }

    def _post(self, endpoint, data):
        try:
            resp = requests.post(
                f"{self.base_url}/api/v1{endpoint}",
                headers=self._headers(),
                json=data, timeout=10,
            )
            return resp.json(), resp.status_code
        except Exception as e:
            print(f"[TheHive] POST {endpoint}: {e}")
            return None, 500

    def _get(self, endpoint, params=None):
        try:
            resp = requests.get(
                f"{self.base_url}/api/v1{endpoint}",
                headers=self._headers(),
                params=params, timeout=10,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[TheHive] GET {endpoint}: {e}")
        return None

    # ══════════════════════════════════════════
    #  CRÉER UNE ALERTE depuis une alerte Wazuh
    # ══════════════════════════════════════════
    def create_alert_from_wazuh(self, wazuh_alert, dossier_ref=None):
        """
        Crée une alerte TheHive depuis une alerte Wazuh.
        Retourne (alerte_dict, status_code)
        """
        level       = wazuh_alert.get('rule', {}).get('level', 1)
        description = wazuh_alert.get('rule', {}).get('description', 'Alerte Wazuh')
        agent_name  = wazuh_alert.get('agent', {}).get('name', 'inconnu')
        agent_ip    = wazuh_alert.get('agent', {}).get('ip', '')
        rule_id     = wazuh_alert.get('rule', {}).get('id', '')
        timestamp   = wazuh_alert.get('timestamp', '')
        full_log    = wazuh_alert.get('full_log', '')

        # Sévérité TheHive : 1=Low, 2=Medium, 3=High, 4=Critical
        severity = self._wazuh_level_to_thehive_severity(int(level))

        tags = ['wazuh', f'rule-{rule_id}', f'agent-{agent_name}']
        if dossier_ref:
            tags.append(f'dossier-{dossier_ref}')

        alert_data = {
            'type':        'wazuh-alert',
            'source':      'wazuh',
            'sourceRef':   f"wazuh-{rule_id}-{timestamp}",
            'title':       f"[Wazuh] {description} — Agent: {agent_name}",
            'description': (
                f"**Alerte Wazuh détectée**\n\n"
                f"- **Règle** : {rule_id} — {description}\n"
                f"- **Agent** : {agent_name} ({agent_ip})\n"
                f"- **Niveau** : {level}/15\n"
                f"- **Horodatage** : {timestamp}\n"
                f"- **Dossier SGD** : {dossier_ref or 'Non lié'}\n\n"
                f"**Log complet** :\n```\n{full_log}\n```"
            ),
            'severity':    severity,
            'tags':        tags,
            'tlp':         2,  # TLP:AMBER
            'pap':         2,
        }

        return self._post('/alert', alert_data)

    def create_case_from_wazuh(self, wazuh_alert, dossier_ref=None):
        """
        Crée directement un cas TheHive (plus grave qu'une alerte).
        """
        level       = wazuh_alert.get('rule', {}).get('level', 1)
        description = wazuh_alert.get('rule', {}).get('description', 'Incident Wazuh')
        agent_name  = wazuh_alert.get('agent', {}).get('name', 'inconnu')
        severity    = self._wazuh_level_to_thehive_severity(int(level))

        case_data = {
            'title':       f"[INCIDENT] {description} — {agent_name}",
            'description': f"Incident créé automatiquement depuis Wazuh.\n\nAgent: {agent_name}\nNiveau: {level}/15\nDossier SGD: {dossier_ref or 'Non lié'}",
            'severity':    severity,
            'tags':        ['wazuh', 'auto-generated', f'agent-{agent_name}'],
            'tlp':         2,
            'pap':         2,
            'flag':        False,
        }

        return self._post('/case', case_data)

    def get_recent_alerts(self, limit=10):
        """Récupère les dernières alertes TheHive."""
        data = self._post('/alert/_search', {
            'query': {'_name': 'listAlert'},
            'range': f'0-{limit}',
            'sort':  ['-_createdAt'],
        })
        return data[0] if data[0] else []

    def is_available(self):
        """Vérifie si TheHive répond."""
        try:
            resp = requests.get(
                f"{self.base_url}/api/v1/status",
                headers=self._headers(), timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    # ══════════════════════════════════════════
    #  HELPER
    # ══════════════════════════════════════════
    @staticmethod
    def _wazuh_level_to_thehive_severity(level):
        if level >= 12:
            return 4   # Critical
        elif level >= 8:
            return 3   # High
        elif level >= 4:
            return 2   # Medium
        else:
            return 1   # Low
