from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.dossiers.models import Dossier, StatutDossier, PrioriteDossier
from apps.users.models import User
from apps.audit.models import ActionLog


@login_required
def home(request):
    now = timezone.now()
    last_7 = now - timedelta(days=7)
    last_30 = now - timedelta(days=30)

    # Dossiers accessibles selon rôle
    if request.user.is_agent:
        qs = Dossier.objects.filter(
            Q(responsable=request.user) | Q(cree_par=request.user)
        )
    else:
        qs = Dossier.objects.all()

    # KPIs
    total_dossiers = qs.count()
    ouverts = qs.filter(statut=StatutDossier.OUVERT).count()
    en_cours = qs.filter(statut=StatutDossier.EN_COURS).count()
    critiques = qs.filter(priorite=PrioriteDossier.CRITIQUE).count()
    en_retard = qs.filter(
        date_echeance__lt=now.date(),
        statut__in=[StatutDossier.OUVERT, StatutDossier.EN_COURS]
    ).count()

    # Dossiers récents
    dossiers_recents = qs.select_related('client', 'responsable').order_by('-created_at')[:8]

    # Répartition par statut (pour graphique)
    statuts_data = list(
        qs.values('statut').annotate(total=Count('id')).order_by('statut')
    )

    # Répartition par priorité
    priorites_data = list(
        qs.values('priorite').annotate(total=Count('id')).order_by('priorite')
    )

    # Activité des 7 derniers jours (dossiers créés par jour)
    activite_data = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        count = qs.filter(
            created_at__date=day.date()
        ).count()
        activite_data.append({'date': day.strftime('%d/%m'), 'count': count})

    # Stats utilisateurs (admin/manager seulement)
    user_stats = None
    if request.user.is_manager:
        user_stats = {
            'total': User.objects.count(),
            'actifs': User.objects.filter(is_active=True).count(),
            'connectes_7j': User.objects.filter(last_login__gte=last_7).count(),
        }

    # Dernières actions audit
    logs_recents = ActionLog.objects.select_related('user').order_by('-timestamp')[:10]

    context = {
        'total_dossiers': total_dossiers,
        'ouverts': ouverts,
        'en_cours': en_cours,
        'critiques': critiques,
        'en_retard': en_retard,
        'dossiers_recents': dossiers_recents,
        'statuts_data': statuts_data,
        'priorites_data': priorites_data,
        'activite_data': activite_data,
        'user_stats': user_stats,
        'logs_recents': logs_recents,
    }
    return render(request, 'dashboard/home.html', context)
