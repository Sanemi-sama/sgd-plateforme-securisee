class AuditMiddleware:
    """Enregistre automatiquement les accès non-authentifiés suspects."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Log les 403 pour détecter les tentatives d'accès non autorisées
        if response.status_code == 403 and request.user.is_authenticated:
            from .utils import log_action
            log_action(
                request.user, 'ACCESS_DENIED',
                f"Accès refusé : {request.path}",
                request=request
            )
        return response
