from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('users/', include('apps.users.urls', namespace='users')),
    path('dossiers/', include('apps.dossiers.urls', namespace='dossiers')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()