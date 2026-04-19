from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api import views

# JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Router API
router = routers.DefaultRouter()
router.register(r'auteurs', views.AuteurViewSet)
router.register(r'livres', views.LivreViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'emprunts', views.EmpruntViewSet)

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # API principale
    path('api/', include(router.urls)),

    # Auth JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Login interface DRF (optionnel)
    path('api-auth/', include('rest_framework.urls')),
]
