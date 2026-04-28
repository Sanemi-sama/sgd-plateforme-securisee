from django.conf import settings

def external_tools(request):
    """
    Expose external tool URLs to all templates.
    """
    return {
        "WAZUH_URL": getattr(settings, "WAZUH_DASHBOARD_URL", "http://localhost:5601"),
        "THEHIVE_URL": getattr(settings, "THEHIVE_EXTERNAL_URL", "http://localhost:9000"),
    }

