from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('', views.dossier_list, name='list'),
    path('creer/', views.dossier_create, name='create'),
    path('<int:pk>/', views.dossier_detail, name='detail'),
    path('<int:pk>/modifier/', views.dossier_update, name='update'),
    path('<int:pk>/supprimer/', views.dossier_delete, name='delete'),
    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/creer/', views.client_create, name='client_create'),
    path('clients/<int:pk>/modifier/', views.client_update, name='client_update'),
]
