"""
Filtres personnalisés.
TP Django REST Framework — Partie 8
"""

import django_filters
from .models import Livre, Emprunt


class LivreFilter(django_filters.FilterSet):
    """
    Filtre avancé pour les livres.

    Exemples d'URL :
        GET /api/livres/?categorie=roman
        GET /api/livres/?annee_min=1990&annee_max=2020
        GET /api/livres/?titre=misérables
        GET /api/livres/?auteur_nom=hugo
        GET /api/livres/?disponible=true
    """
    categorie = django_filters.ChoiceFilter(choices=Livre.CATEGORIES)
    annee_min = django_filters.NumberFilter(
        field_name='annee_publication', lookup_expr='gte'
    )
    annee_max = django_filters.NumberFilter(
        field_name='annee_publication', lookup_expr='lte'
    )
    titre = django_filters.CharFilter(lookup_expr='icontains')
    auteur_nom = django_filters.CharFilter(
        field_name='auteur__nom', lookup_expr='icontains'
    )
    disponible = django_filters.BooleanFilter()

    class Meta:
        model = Livre
        fields = ['categorie', 'disponible']


class EmpruntFilter(django_filters.FilterSet):
    """
    Filtre pour les emprunts.

    Exemples :
        GET /api/emprunts/?rendu=false
        GET /api/emprunts/?livre=1
    """
    rendu = django_filters.BooleanFilter()
    livre = django_filters.NumberFilter(field_name='livre__id')

    class Meta:
        model = Emprunt
        fields = ['rendu', 'livre']
