"""
Classes de pagination.
TP Django REST Framework — Partie 8
"""

from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination,
)


class StandardPagination(PageNumberPagination):
    """
    Pagination par numéro de page.
    URL : /api/livres/?page=2&size=5
    """
    page_size = 10
    page_size_query_param = 'size'   # ?size=20 pour surcharger
    max_page_size = 100


class FlexiblePagination(LimitOffsetPagination):
    """
    Pagination par limite/offset.
    URL : /api/livres/?limit=10&offset=20
    """
    default_limit = 10
    max_limit = 50


class PerformantePagination(CursorPagination):
    """
    Pagination par curseur — très performante pour grands datasets.
    Recommandée pour les flux temps-réel (pas de COUNT SQL).
    URL : /api/livres/?cursor=cD0yMDIz...
    """
    page_size = 10
    ordering = '-date_creation'
