"""
Script pour peupler la base de données avec des données de test.
Lancer avec : python manage.py shell < seed_data.py
Ou : python seed_data.py (depuis la racine du projet avec Django configuré)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheque_project.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Auteur, Livre, Tag, Emprunt
from datetime import date, timedelta

print("Création des données de test...")

# ─── Superutilisateur ──────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@exemple.com', 'admin1234')
    print("Superutilisateur 'admin' créé (mot de passe : admin1234)")
else:
    admin = User.objects.get(username='admin')
    print("Superutilisateur 'admin' existant.")

# ─── Tags ──────────────────────────────────────────────────────────────────
tags_data = ['classique', 'philosophie', 'drame', 'aventure', 'dystopie', 'amour']
tags = {nom: Tag.objects.get_or_create(nom=nom)[0] for nom in tags_data}
print(f"{len(tags)} tags créés.")

# ─── Auteurs ───────────────────────────────────────────────────────────────
auteurs_data = [
    {
        'nom': 'Victor Hugo',
        'nationalite': 'Française',
        'biographie': 'Romancier, poète et dramaturge romantique français (1802-1885).'
    },
    {
        'nom': 'Albert Camus',
        'nationalite': 'Française',
        'biographie': 'Romancier, essayiste et philosophe français (1913-1960). Prix Nobel 1957.'
    },
    {
        'nom': 'George Orwell',
        'nationalite': 'Britannique',
        'biographie': 'Romancier et essayiste britannique (1903-1950), auteur de 1984.'
    },
    {
        'nom': 'Jules Verne',
        'nationalite': 'Française',
        'biographie': 'Romancier français pionnier de la science-fiction (1828-1905).'
    },
]

auteurs = {}
for data in auteurs_data:
    auteur, _ = Auteur.objects.get_or_create(nom=data['nom'], defaults=data)
    auteurs[data['nom']] = auteur
print(f"{len(auteurs)} auteurs créés.")

# ─── Livres ────────────────────────────────────────────────────────────────
livres_data = [
    {
        'titre': 'Les Misérables',
        'isbn': '9782070409228',
        'annee_publication': 1862,
        'categorie': 'roman',
        'auteur': auteurs['Victor Hugo'],
        'tags_list': ['classique', 'drame'],
        'disponible': True,
    },
    {
        'titre': 'Notre-Dame de Paris',
        'isbn': '9782070409235',
        'annee_publication': 1831,
        'categorie': 'roman',
        'auteur': auteurs['Victor Hugo'],
        'tags_list': ['classique', 'drame'],
        'disponible': True,
    },
    {
        'titre': "L'Étranger",
        'isbn': '9782070360024',
        'annee_publication': 1942,
        'categorie': 'roman',
        'auteur': auteurs['Albert Camus'],
        'tags_list': ['classique', 'philosophie'],
        'disponible': True,
    },
    {
        'titre': 'La Peste',
        'isbn': '9782070360031',
        'annee_publication': 1947,
        'categorie': 'roman',
        'auteur': auteurs['Albert Camus'],
        'tags_list': ['classique', 'philosophie'],
        'disponible': False,
    },
    {
        'titre': '1984',
        'isbn': '9782070368228',
        'annee_publication': 1949,
        'categorie': 'roman',
        'auteur': auteurs['George Orwell'],
        'tags_list': ['dystopie', 'classique'],
        'disponible': True,
    },
    {
        'titre': 'Le Tour du monde en 80 jours',
        'isbn': '9782013224321',
        'annee_publication': 1872,
        'categorie': 'roman',
        'auteur': auteurs['Jules Verne'],
        'tags_list': ['aventure', 'classique'],
        'disponible': True,
    },
    {
        'titre': 'Vingt mille lieues sous les mers',
        'isbn': '9782013224338',
        'annee_publication': 1870,
        'categorie': 'roman',
        'auteur': auteurs['Jules Verne'],
        'tags_list': ['aventure'],
        'disponible': True,
    },
]

livres = {}
for data in livres_data:
    tags_list = data.pop('tags_list')
    livre, created = Livre.objects.get_or_create(
        isbn=data['isbn'],
        defaults={**data, 'cree_par': admin}
    )
    livre.tags.set([tags[t] for t in tags_list])
    livres[data['titre']] = livre
print(f"{len(livres)} livres créés.")

# ─── Emprunt ───────────────────────────────────────────────────────────────
livre_emprunte = livres['La Peste']
if not Emprunt.objects.filter(utilisateur=admin, livre=livre_emprunte).exists():
    Emprunt.objects.create(
        utilisateur=admin,
        livre=livre_emprunte,
        date_retour_prevue=date.today() + timedelta(days=14),
    )
    print("Emprunt de test créé.")

print("\n✓ Données de test chargées avec succès !")
print("  Superuser : admin / admin1234")
print("  Admin Django : http://127.0.0.1:8000/admin/")
print("  API racine   : http://127.0.0.1:8000/api/")
