from django.urls import path
from . import views
from . import wazuh_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    # Wazuh
    path('wazuh/alertes/',   wazuh_views.wazuh_alerts,    name='wazuh_alerts'),
    path('wazuh/dashboard/', wazuh_views.wazuh_dashboard,  name='wazuh_dashboard'),
    path('wazuh/thehive/',   wazuh_views.send_to_thehive,  name='send_to_thehive'),
    path('wazuh/status/',    wazuh_views.wazuh_status,     name='wazuh_status'),
]
