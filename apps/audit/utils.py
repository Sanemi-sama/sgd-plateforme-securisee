from .models import ActionLog


def log_action(user, action, description='', request=None):
    """Helper pour journaliser une action depuis n'importe où."""
    ip = None
    user_agent = ''
    path = ''
    method = ''

    if request:
        ip_raw = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        ip = ip_raw.split(',')[0].strip() if ip_raw else None
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        path = request.path
        method = request.method

    ActionLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip,
        user_agent=user_agent,
        path=path,
        method=method,
    )
