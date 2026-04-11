"""
Sérialiseurs de l'API Bibliothèque.
TP Django REST Framework — Partie 3 & 7
"""

from rest_framework import serializers
from .models import Auteur, Livre, Tag, Emprunt, ProfilLecteur


# ─── Tag ────────────────────────────────────────────────────────────────────

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nom']


# ─── Auteur ─────────────────────────────────────────────────────────────────

class AuteurSerializer(serializers.ModelSerializer):
    """Sérialiseur principal pour les auteurs."""
    # Champ calculé : nombre de livres de l'auteur
    nombre_livres = serializers.SerializerMethodField()

    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'biographie', 'nationalite', 'nombre_livres', 'date_creation']
        read_only_fields = ['id', 'date_creation']

    def get_nombre_livres(self, obj):
        return obj.livres.count()


class AuteurListSerializer(serializers.ModelSerializer):
    """Sérialiseur allégé pour les listes."""
    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'nationalite']


# ─── Livre ───────────────────────────────────────────────────────────────────

class LivreSerializer(serializers.ModelSerializer):
    """Sérialiseur principal pour les livres (création / mise à jour)."""
    # Lecture : affiche le nom de l'auteur
    auteur_nom = serializers.SerializerMethodField()
    # Lecture : liste des tags imbriqués
    tags = TagSerializer(many=True, read_only=True)
    # Écriture : ID de l'auteur
    auteur_id = serializers.PrimaryKeyRelatedField(
        queryset=Auteur.objects.all(),
        source='auteur',
        write_only=True
    )
    # Écriture : liste d'IDs de tags
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication', 'categorie',
            'disponible', 'auteur_id', 'auteur_nom', 'tags', 'tag_ids',
            'date_creation'
        ]
        read_only_fields = ['id', 'date_creation']

    def get_auteur_nom(self, obj):
        return obj.auteur.nom

    def validate_isbn(self, value):
        """L'ISBN doit contenir exactement 13 chiffres."""
        clean = value.replace('-', '')
        if not clean.isdigit() or len(clean) != 13:
            raise serializers.ValidationError(
                "L'ISBN doit contenir exactement 13 chiffres."
            )
        return value

    def validate_annee_publication(self, value):
        """L'année doit être dans une plage raisonnable."""
        if value < 1000 or value > 2100:
            raise serializers.ValidationError(
                "L'année doit être entre 1000 et 2100."
            )
        return value

    def validate(self, data):
        """Validation cross-champs : les essais requièrent une biographie."""
        if data.get('categorie') == 'essai':
            auteur = data.get('auteur')
            if auteur and not auteur.biographie:
                raise serializers.ValidationError(
                    "Les essais requièrent une biographie de l'auteur."
                )
        return data


class LivreDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur détaillé avec auteur et tags imbriqués (lecture seule)."""
    auteur = AuteurSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cree_par = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication', 'categorie',
            'disponible', 'auteur', 'tags', 'cree_par', 'date_creation'
        ]


# ─── Auteur avec livres imbriqués ────────────────────────────────────────────

class AuteurAvecLivresSerializer(serializers.ModelSerializer):
    """
    Permet de créer un auteur ET ses livres en une seule requête POST.
    """
    livres = LivreSerializer(many=True, required=False)

    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'nationalite', 'biographie', 'livres']

    def create(self, validated_data):
        livres_data = validated_data.pop('livres', [])
        auteur = Auteur.objects.create(**validated_data)
        for livre_data in livres_data:
            tags_data = livre_data.pop('tags', [])
            livre = Livre.objects.create(auteur=auteur, **livre_data)
            livre.tags.set(tags_data)
        return auteur


# ─── Emprunt ────────────────────────────────────────────────────────────────

class EmpruntSerializer(serializers.ModelSerializer):
    livre_titre = serializers.SerializerMethodField()
    utilisateur_nom = serializers.SerializerMethodField()

    class Meta:
        model = Emprunt
        fields = [
            'id', 'utilisateur', 'utilisateur_nom', 'livre', 'livre_titre',
            'date_emprunt', 'date_retour_prevue', 'rendu'
        ]
        read_only_fields = ['id', 'date_emprunt', 'utilisateur']

    def get_livre_titre(self, obj):
        return obj.livre.titre

    def get_utilisateur_nom(self, obj):
        return obj.utilisateur.username

    def validate(self, data):
        livre = data.get('livre')
        if livre and not livre.disponible:
            raise serializers.ValidationError("Ce livre n'est pas disponible.")
        if data.get('date_retour_prevue') and data.get('date_emprunt'):
            if data['date_retour_prevue'] < data['date_emprunt']:
                raise serializers.ValidationError(
                    "La date de retour doit être postérieure à la date d'emprunt."
                )
        return data


# ─── Profil lecteur ──────────────────────────────────────────────────────────

class ProfilLecteurSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    livres_favoris = LivreSerializer(many=True, read_only=True)
    livres_favoris_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Livre.objects.all(),
        source='livres_favoris',
        write_only=True,
        required=False
    )

    class Meta:
        model = ProfilLecteur
        fields = [
            'id', 'username', 'adresse', 'telephone', 'date_naissance',
            'livres_favoris', 'livres_favoris_ids'
        ]
        read_only_fields = ['id', 'username']

    def get_username(self, obj):
        return obj.utilisateur.username
