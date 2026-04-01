from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q

from .models import ActionLog
from apps.users.views import require_manager


@login_required
@require_manager
def audit_list(request):
    logs = ActionLog.objects.select_related('user').all()

    q = request.GET.get('q', '')
    action = request.GET.get('action', '')
    user_id = request.GET.get('user', '')

    if q:
        logs = logs.filter(Q(description__icontains=q) | Q(user__username__icontains=q))
    if action:
        logs = logs.filter(action=action)
    if user_id:
        logs = logs.filter(user_id=user_id)

    paginator = Paginator(logs, 50)
    page = paginator.get_page(request.GET.get('page'))

    from apps.users.models import User
    context = {
        'page_obj': page,
        'actions': ActionLog.ACTIONS,
        'users': User.objects.all(),
        'q': q, 'action': action, 'user_id': user_id,
    }
    return render(request, 'audit/audit_list.html', context)
