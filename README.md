# API Bibliothèque — TP Django REST Framework

Projet complet du TP DRF couvrant les Parties 1 à 9.

---

## Installation & Lancement

```bash
# 1. Créer et activer l'environnement virtuel
python -m venv env_bibliotheque
source env_bibliotheque/bin/activate       # Linux / Mac
env_bibliotheque\Scripts\activate           # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Appliquer les migrations
python manage.py makemigrations api
python manage.py migrate

# 4. Charger les données de test (auteurs, livres, tags)
python seed_data.py

# 5. Lancer le serveur
python manage.py runserver
```

Accès :
- **API racine** : http://127.0.0.1:8000/api/
- **Admin Django** : http://127.0.0.1:8000/admin/ (admin / admin1234)

---

## Endpoints disponibles

### Authentification JWT
| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/auth/token/` | Obtenir access + refresh token |
| POST | `/api/auth/token/refresh/` | Renouveler le token |

### Auteurs
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/auteurs/` | Liste paginée |
| POST | `/api/auteurs/` | Créer un auteur |
| GET | `/api/auteurs/{id}/` | Détail |
| PUT/PATCH | `/api/auteurs/{id}/` | Modifier |
| DELETE | `/api/auteurs/{id}/` | Supprimer |
| GET | `/api/auteurs/{id}/livres/` | Livres d'un auteur |
| GET | `/api/auteurs/stats/` | Statistiques globales |
| POST | `/api/auteurs/avec-livres/` | Créer auteur + livres |

### Livres
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/livres/` | Liste paginée + filtrée |
| POST | `/api/livres/` | Créer un livre |
| GET | `/api/livres/{id}/` | Détail avec auteur imbriqué |
| PATCH | `/api/livres/{id}/` | Modification partielle |
| DELETE | `/api/livres/{id}/` | Supprimer |
| GET | `/api/livres/disponibles/` | Livres disponibles |
| POST | `/api/livres/{id}/emprunter/` | Emprunter un livre |
| POST | `/api/livres/{id}/rendre/` | Rendre un livre |

### Tags, Emprunts, Profil
| Méthode | URL | Description |
|---------|-----|-------------|
| GET/POST | `/api/tags/` | CRUD tags |
| GET/POST | `/api/emprunts/` | Mes emprunts |
| GET/PUT | `/api/profil/` | Mon profil lecteur |

---

## Paramètres de filtrage (Livres)

```
GET /api/livres/?categorie=roman
GET /api/livres/?annee_min=1900&annee_max=1950
GET /api/livres/?search=hugo
GET /api/livres/?ordering=-annee_publication
GET /api/livres/?disponible=true&page=2&size=5
GET /api/livres/?auteur_nom=camus
```

---

## Tester l'API avec curl

```bash
# 1. Obtenir un token JWT
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "admin", "password": "admin1234"}'

# 2. Lister les livres (public)
curl http://127.0.0.1:8000/api/livres/

# 3. Créer un auteur (avec token)
curl -X POST http://127.0.0.1:8000/api/auteurs/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <votre_token>' \
  -d '{"nom": "Molière", "nationalite": "Française"}'

# 4. Emprunter un livre
curl -X POST http://127.0.0.1:8000/api/livres/1/emprunter/ \
  -H 'Authorization: Bearer <votre_token>'

# 5. Filtrer les livres
curl "http://127.0.0.1:8000/api/livres/?search=hugo&ordering=-annee_publication"
```

---

## Lancer les tests

```bash
python manage.py test api
```

---

## Structure du projet

```
bibliotheque_project/
├── manage.py
├── requirements.txt
├── seed_data.py           ← données de test
├── bibliotheque_project/
│   ├── settings.py        ← config DRF, JWT, BDD
│   └── urls.py            ← URLs principales
└── api/
    ├── models.py          ← Auteur, Livre, Tag, Emprunt, ProfilLecteur
    ├── serializers.py     ← sérialiseurs avec validation
    ├── views.py           ← ViewSets + vues personnalisées
    ├── permissions.py     ← EstProprietaireOuReadOnly
    ├── filters.py         ← LivreFilter, EmpruntFilter
    ├── pagination.py      ← StandardPagination, Cursor...
    ├── urls.py            ← Router + JWT + endpoints
    ├── admin.py           ← interface d'administration
    └── tests.py           ← tests automatisés APITestCase
```

---

## Concepts couverts

- ✅ Modèles Django (ForeignKey, ManyToMany, OneToOne)
- ✅ Migrations
- ✅ Sérialiseurs (ModelSerializer, validation, champs imbriqués)
- ✅ Vues (APIView, GenericView, ViewSet)
- ✅ Router DRF et génération automatique des URLs
- ✅ Authentification JWT (SimpleJWT)
- ✅ Permissions personnalisées
- ✅ Pagination (PageNumber, LimitOffset, Cursor)
- ✅ Filtres (DjangoFilterBackend, SearchFilter, OrderingFilter)
- ✅ Actions personnalisées (@action)
- ✅ Optimisation SQL (select_related, prefetch_related)
- ✅ Tests automatisés (APITestCase)
