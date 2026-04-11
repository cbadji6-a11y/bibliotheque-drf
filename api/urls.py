"""
Configuration des URLs de l'API Bibliothèque.
TP Django REST Framework — Partie 5
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AuteurViewSet, LivreViewSet, TagViewSet, EmpruntViewSet,
    AuteurListAPIView, LivreListCreateView, ProfilView,
)

# ─── Router (Niveau 3 — ViewSets) ────────────────────────────────────────────
router = DefaultRouter()
router.register(r'auteurs',  AuteurViewSet,  basename='auteur')
router.register(r'livres',   LivreViewSet,   basename='livre')
router.register(r'tags',     TagViewSet,     basename='tag')
router.register(r'emprunts', EmpruntViewSet, basename='emprunt')

# URLs générées automatiquement :
# GET    /api/auteurs/              → list
# POST   /api/auteurs/              → create
# GET    /api/auteurs/{pk}/         → retrieve
# PUT    /api/auteurs/{pk}/         → update
# PATCH  /api/auteurs/{pk}/         → partial_update
# DELETE /api/auteurs/{pk}/         → destroy
# GET    /api/auteurs/{pk}/livres/  → action livres
# GET    /api/auteurs/stats/        → action stats
# POST   /api/auteurs/avec-livres/  → action avec_livres
# GET    /api/livres/disponibles/   → action disponibles
# POST   /api/livres/{pk}/emprunter/ → action emprunter
# POST   /api/livres/{pk}/rendre/   → action rendre

urlpatterns = [
    # ── Authentification JWT ────────────────────────────────────────────
    path('auth/token/',         TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),   name='token_refresh'),

    # ── Profil utilisateur ──────────────────────────────────────────────
    path('profil/', ProfilView.as_view(), name='profil'),

    # ── Exemples Niveau 1 & 2 (Parties 4.2 et 4.3) ─────────────────────
    path('auteurs-simple/', AuteurListAPIView.as_view(),  name='auteur-simple-list'),
    path('livres-generic/', LivreListCreateView.as_view(), name='livre-generic-list'),

    # ── ViewSets via Router (Niveau 3) ──────────────────────────────────
    path('', include(router.urls)),
]
