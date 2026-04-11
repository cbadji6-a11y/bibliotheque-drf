"""
Tests automatisés de l'API Bibliothèque.
TP Django REST Framework — Défi Final (Partie 9)

Lancer avec : python manage.py test api
"""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Auteur, Livre, Tag


class AuteurTests(APITestCase):
    """Tests pour l'endpoint /api/auteurs/."""

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.auteur = Auteur.objects.create(nom='Victor Hugo', nationalite='Française')

    def test_liste_auteurs_public(self):
        """GET /api/auteurs/ accessible sans authentification."""
        response = self.client.get('/api/auteurs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_creer_auteur_authentifie(self):
        """POST /api/auteurs/ nécessite une authentification."""
        self.client.force_authenticate(user=self.admin)
        data = {'nom': 'Albert Camus', 'nationalite': 'Française'}
        response = self.client.post('/api/auteurs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nom'], 'Albert Camus')

    def test_creer_auteur_non_authentifie(self):
        """POST /api/auteurs/ échoue sans authentification (401)."""
        data = {'nom': 'Molière', 'nationalite': 'Française'}
        response = self.client.post('/api/auteurs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_auteur(self):
        """GET /api/auteurs/{pk}/ retourne le bon auteur."""
        response = self.client.get(f'/api/auteurs/{self.auteur.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], 'Victor Hugo')

    def test_stats_auteurs(self):
        """GET /api/auteurs/stats/ retourne les statistiques."""
        response = self.client.get('/api/auteurs/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_auteurs', response.data)
        self.assertIn('total_livres', response.data)


class LivreTests(APITestCase):
    """Tests pour l'endpoint /api/livres/."""

    def setUp(self):
        self.user = User.objects.create_user('lecteur', 'l@l.com', 'pass')
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.auteur = Auteur.objects.create(nom='Jules Verne', nationalite='Française')
        self.livre = Livre.objects.create(
            titre='1984',
            isbn='9782070368228',
            annee_publication=1949,
            auteur=self.auteur,
            disponible=True,
            cree_par=self.admin,
        )

    def test_liste_livres_publique(self):
        """GET /api/livres/ accessible sans authentification."""
        response = self.client.get('/api/livres/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_creer_livre(self):
        """POST /api/livres/ crée un livre correctement."""
        self.client.force_authenticate(user=self.user)
        data = {
            'titre': 'Le Tour du monde en 80 jours',
            'isbn': '9782013224321',
            'annee_publication': 1872,
            'categorie': 'roman',
            'auteur_id': self.auteur.pk,
        }
        response = self.client.post('/api/livres/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_isbn_invalide(self):
        """POST avec ISBN invalide retourne une erreur 400."""
        self.client.force_authenticate(user=self.user)
        data = {
            'titre': 'Test',
            'isbn': 'INVALIDE',
            'annee_publication': 2020,
            'auteur_id': self.auteur.pk,
        }
        response = self.client.post('/api/livres/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('isbn', response.data)

    def test_emprunter_livre_disponible(self):
        """POST /api/livres/{pk}/emprunter/ marque le livre indisponible."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/livres/{self.livre.pk}/emprunter/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.livre.refresh_from_db()
        self.assertFalse(self.livre.disponible)

    def test_emprunter_livre_indisponible(self):
        """POST /api/livres/{pk}/emprunter/ échoue si déjà emprunté."""
        self.livre.disponible = False
        self.livre.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/livres/{self.livre.pk}/emprunter/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtre_par_categorie(self):
        """GET /api/livres/?categorie=roman filtre correctement."""
        response = self.client.get('/api/livres/?categorie=roman')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_livres_disponibles(self):
        """GET /api/livres/disponibles/ retourne seulement les disponibles."""
        response = self.client.get('/api/livres/disponibles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for livre in response.data.get('results', response.data):
            self.assertTrue(livre['disponible'])
