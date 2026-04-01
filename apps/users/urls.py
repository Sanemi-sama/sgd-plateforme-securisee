from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.user_list, name='list'),
    path('creer/', views.user_create, name='create'),
    path('<int:pk>/modifier/', views.user_update, name='update'),
    path('<int:pk>/supprimer/', views.user_delete, name='delete'),
    path('profil/', views.profile, name='profile'),
    path('mot-de-passe/', views.change_password, name='change_password'),
]
