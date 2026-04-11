"""
Permissions personnalisées.
TP Django REST Framework — Partie 6
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class EstProprietaireOuReadOnly(BasePermission):
    """
    Lecture libre pour tous.
    Modification uniquement par le créateur ou un admin (is_staff).
    Le modèle doit avoir un champ 'cree_par' ForeignKey vers User.
    """
    message = 'Vous devez être le propriétaire pour modifier cet objet.'

    def has_permission(self, request, view):
        # Méthodes sûres (GET, HEAD, OPTIONS) → toujours autorisé
        if request.method in SAFE_METHODS:
            return True
        # Écriture → doit être authentifié
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Lecture toujours autorisée
        if request.method in SAFE_METHODS:
            return True
        # Modification : propriétaire ou admin
        if hasattr(obj, 'cree_par'):
            return obj.cree_par == request.user or request.user.is_staff
        return request.user.is_staff


class EstUtilisateurOuAdmin(BasePermission):
    """
    Permet à un utilisateur de voir/modifier uniquement ses propres ressources.
    Les admins (is_staff) ont accès à tout.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'utilisateur'):
            return obj.utilisateur == request.user
        return False
