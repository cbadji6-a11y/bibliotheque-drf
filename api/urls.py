from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.urls import include, path

router = DefaultRouter()

router.register(r'auteurs', views.AuteurViewSet)
router.register(r'livres', views.LivreViewSet)
router.register(r'tags', views.TagViewSet)

# 🔥 IMPORTANT : ajouter basename ici
router.register(r'emprunts', views.EmpruntViewSet, basename='emprunt')


urlpatterns = [
    path('api/', include('monapp.urls')),  # La racine de votre API est /api/
]