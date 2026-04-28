from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
import json

from .wazuh_service import WazuhService
from .thehive_service import TheHiveService
from apps.audit.utils import log_action
from apps.users.views import require_manager


@login_required
@require_manager
def wazuh_alerts(request):
    """Page principale des alertes Wazuh."""
    wazuh = WazuhService()

    min_level = request.GET.get('level', '')
    limit     = int(request.GET.get('limit', 20))

    wazuh_disponible = wazuh.is_available()
    alerts           = []
    summary          = {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    agents_summary   = {'active': 0, 'disconnected': 0, 'total': 0}

    if wazuh_disponible:
        alerts         = wazuh.get_alerts(limit=limit, min_level=min_level or None)
        summary        = wazuh.get_alerts_summary()
        agents_summary = wazuh.get_agents_summary()
        for alert in alerts:
            level = alert.get('rule', {}).get('level', 1)
            sev_label, sev_class = WazuhService.level_to_severity(level)
            # Django templates cannot access keys starting with "_"
            alert['severity_label'] = sev_label
            alert['severity_class'] = sev_class

    log_action(request.user, 'OTHER', "Consultation des alertes Wazuh")

    return render(request, 'dashboard/wazuh_alerts.html', {
        'alerts':           alerts,
        'alerts_json':      json.dumps(alerts),
        'summary':          summary,
        'agents_summary':   agents_summary,
        'wazuh_disponible': wazuh_disponible,
        'min_level':        min_level,
        'limit':            limit,
    })


@login_required
@require_manager
def send_to_thehive(request):
    """Envoie une alerte Wazuh vers TheHive (POST AJAX)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        body        = json.loads(request.body)
        wazuh_alert = body.get('alert', {})
        dossier_ref = body.get('dossier_ref', None)
        create_case = body.get('create_case', False)

        thehive = TheHiveService()

        if not thehive.is_available():
            return JsonResponse({'error': 'TheHive non disponible'}, status=503)

        if create_case:
            result, status = thehive.create_case_from_wazuh(wazuh_alert, dossier_ref)
            action_type = 'Cas'
        else:
            result, status = thehive.create_alert_from_wazuh(wazuh_alert, dossier_ref)
            action_type = 'Alerte'

        if status in (200, 201):
            log_action(
                request.user, 'OTHER',
                f"{action_type} TheHive créé depuis alerte Wazuh — règle {wazuh_alert.get('rule', {}).get('id', '?')}"
            )
            return JsonResponse({
                'success': True,
                'message': f"{action_type} créé dans TheHive avec succès !",
                'thehive_id': result.get('_id', '') if result else '',
            })
        else:
            return JsonResponse({'error': f'Erreur TheHive : {status}'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_manager
def wazuh_status(request):
    """API JSON — statut Wazuh pour le dashboard graphique."""
    wazuh = WazuhService()
    if wazuh.is_available():
        # Récupère la liste des agents avec détails
        agents_raw    = wazuh.get_agents()
        agents_list   = [
            {
                'name':   a.get('name', 'Agent'),
                'ip':     a.get('registerIP', a.get('ip', '')),
                'status': a.get('status', 'inactive'),
                'os':     a.get('os', {}).get('name', ''),
                'id':     a.get('id', ''),
            }
            for a in agents_raw
        ]
        return JsonResponse({
            'available':    True,
            'summary':      wazuh.get_alerts_summary(),
            'agents':       wazuh.get_agents_summary(),
            'agents_list':  agents_list,
        })
    return JsonResponse({'available': False})


@login_required
@require_manager
def wazuh_dashboard(request):
    """Page dashboard sécurité avec graphiques dynamiques."""
    log_action(request.user, 'OTHER', "Consultation du dashboard sécurité Wazuh")
    return render(request, 'dashboard/wazuh_dashboard.html')
