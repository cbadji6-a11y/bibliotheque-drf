"""
Interface d'administration Django.
TP Django REST Framework — Partie 2
"""

from django.contrib import admin
from .models import Auteur, Livre, Tag, Emprunt, ProfilLecteur


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nationalite', 'date_creation']
    search_fields = ['nom', 'nationalite']
    list_filter = ['nationalite']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'annee_publication', 'categorie', 'disponible', 'cree_par']
    list_filter = ['categorie', 'disponible', 'annee_publication']
    search_fields = ['titre', 'isbn', 'auteur__nom']
    filter_horizontal = ['tags']
   


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'livre', 'date_emprunt', 'date_retour_prevue', 'rendu']
    list_filter = ['rendu']
    search_fields = ['utilisateur__username', 'livre__titre']


@admin.register(ProfilLecteur)
class ProfilLecteurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'telephone']
    search_fields = ['utilisateur__username']
    filter_horizontal = ['livres_favoris']
