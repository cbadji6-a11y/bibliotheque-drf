"""
Vues de l'API Bibliothèque.
TP Django REST Framework — Parties 4, 6, 7, 9
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Auteur, Livre, Tag, Emprunt, ProfilLecteur
from .serializers import (
    AuteurSerializer, AuteurListSerializer, AuteurAvecLivresSerializer,
    LivreSerializer, LivreDetailSerializer,
    TagSerializer, EmpruntSerializer, ProfilLecteurSerializer,
)
from .permissions import EstProprietaireOuReadOnly, EstUtilisateurOuAdmin
from .filters import LivreFilter, EmpruntFilter
from .pagination import StandardPagination


# ─── EXEMPLE NIVEAU 1 : APIView ──────────────────────────────────────────────

class AuteurListAPIView(APIView):
    """
    Exemple Partie 4.2 — Vue de bas niveau avec APIView.
    GET  /api/auteurs-simple/   → liste
    POST /api/auteurs-simple/   → création
    """
    def get(self, request):
        auteurs = Auteur.objects.all()
        serializer = AuteurListSerializer(auteurs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AuteurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── EXEMPLE NIVEAU 2 : Generic Views ────────────────────────────────────────

class LivreListCreateView(generics.ListCreateAPIView):
    """
    Exemple Partie 4.3 — Generic View.
    GET  /api/livres-generic/  → liste
    POST /api/livres-generic/  → création
    """
    queryset = Livre.objects.all().select_related('auteur')
    serializer_class = LivreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(cree_par=self.request.user)


# ─── NIVEAU 3 : ViewSets ────────────────────────────────────────────────────

class AuteurViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour les auteurs.
    Routes générées automatiquement par le Router.
    """
    queryset = Auteur.objects.all().prefetch_related('livres')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return AuteurListSerializer
        if self.action == 'avec_livres':
            return AuteurAvecLivresSerializer
        return AuteurSerializer

    # Action : GET /api/auteurs/{pk}/livres/
    @action(detail=True, methods=['get'], url_path='livres')
    def livres(self, request, pk=None):
        """Retourne tous les livres d'un auteur spécifique."""
        auteur = self.get_object()
        livres = auteur.livres.all().prefetch_related('tags')
        serializer = LivreSerializer(livres, many=True)
        return Response(serializer.data)

    # Action : GET /api/auteurs/stats/
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques globales sur les auteurs et livres."""
        from django.db.models import Count, Avg
        data = {
            'total_auteurs': Auteur.objects.count(),
            'total_livres': Livre.objects.count(),
            'total_tags': Tag.objects.count(),
            'livres_disponibles': Livre.objects.filter(disponible=True).count(),
            'nationalites': list(
                Auteur.objects.values_list('nationalite', flat=True)
                .exclude(nationalite='').distinct()
            ),
            'categories': dict(
                Livre.objects.values_list('categorie')
                .annotate(nb=Count('categorie'))
                .values_list('categorie', 'nb')
            ),
        }
        return Response(data)

    # Action : POST /api/auteurs/avec_livres/
    @action(detail=False, methods=['post'], url_path='avec-livres')
    def avec_livres(self, request):
        """Créer un auteur avec ses livres en une seule requête."""
        serializer = AuteurAvecLivresSerializer(data=request.data)
        if serializer.is_valid():
            auteur = serializer.save()
            return Response(
                AuteurSerializer(auteur).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LivreViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour les livres — version finale Partie 9.
    Inclut : pagination, filtres, permissions, actions personnalisées.
    """
    queryset = (
        Livre.objects
        .select_related('auteur', 'cree_par')
        .prefetch_related('tags')
        .all()
    )
    permission_classes = [EstProprietaireOuReadOnly]
    pagination_class = StandardPagination
    filterset_class = LivreFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['titre', 'auteur__nom', 'isbn']
    ordering_fields = ['titre', 'annee_publication', 'date_creation']
    ordering = ['-date_creation']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LivreDetailSerializer
        return LivreSerializer

    def get_permissions(self):
        """Permissions différentes selon l'action."""
        if self.action == 'list':
            return [AllowAny()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Enregistre automatiquement l'utilisateur connecté comme créateur."""
        serializer.save(cree_par=self.request.user)

    # Action : GET /api/livres/disponibles/
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Retourne uniquement les livres disponibles (paginés)."""
        qs = self.get_queryset().filter(disponible=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # Action : POST /api/livres/{pk}/emprunter/
    @action(detail=True, methods=['post'])
    def emprunter(self, request, pk=None):
        """Emprunter un livre — le marque comme indisponible."""
        livre = self.get_object()
        if not livre.disponible:
            return Response(
                {'erreur': "Ce livre n'est pas disponible."},
                status=status.HTTP_400_BAD_REQUEST
            )
        livre.disponible = False
        livre.save()
        return Response({'message': f'Livre "{livre.titre}" emprunté avec succès.'})

    # Action : POST /api/livres/{pk}/rendre/
    @action(detail=True, methods=['post'])
    def rendre(self, request, pk=None):
        """Rendre un livre — le marque comme disponible."""
        livre = self.get_object()
        livre.disponible = True
        livre.save()
        return Response({'message': f'Livre "{livre.titre}" rendu avec succès.'})


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet pour les tags."""
    queryset = Tag.objects.all().prefetch_related('livres')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def livres(self, request, pk=None):
        """Livres associés à un tag."""
        tag = self.get_object()
        serializer = LivreSerializer(tag.livres.all(), many=True)
        return Response(serializer.data)


class EmpruntViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les emprunts.
    Chaque utilisateur ne voit que ses propres emprunts.
    """
    serializer_class = EmpruntSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EmpruntFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['date_emprunt', 'date_retour_prevue']
    ordering = ['-date_emprunt']

    def get_queryset(self):
        """Filtre automatiquement sur l'utilisateur connecté."""
        if self.request.user.is_staff:
            return Emprunt.objects.all().select_related('utilisateur', 'livre')
        return Emprunt.objects.filter(
            utilisateur=self.request.user
        ).select_related('utilisateur', 'livre')

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


class ProfilView(generics.RetrieveUpdateAPIView):
    """
    Profil de l'utilisateur connecté.
    GET  /api/profil/  → voir son profil
    PUT  /api/profil/  → mettre à jour son profil
    """
    serializer_class = ProfilLecteurSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profil, _ = ProfilLecteur.objects.get_or_create(
            utilisateur=self.request.user
        )
        return profil

    @action(detail=False, methods=['post'], url_path='favoris')
    def ajouter_favori(self, request):
        """POST /api/profil/favoris/ → ajouter un livre aux favoris."""
        profil, _ = ProfilLecteur.objects.get_or_create(utilisateur=request.user)
        livre_id = request.data.get('livre_id')
        try:
            livre = Livre.objects.get(pk=livre_id)
            profil.livres_favoris.add(livre)
            return Response({'message': f'"{livre.titre}" ajouté aux favoris.'})
        except Livre.DoesNotExist:
            return Response(
                {'erreur': 'Livre introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )
