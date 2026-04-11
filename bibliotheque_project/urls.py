"""URL configuration principale du projet bibliothèque."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Toutes les URLs de notre API sous le préfixe /api/
    path('api/', include('api.urls')),
    # Navigateur d'API DRF (interface web pour tester)
    path('api-auth/', include('rest_framework.urls')),
]
