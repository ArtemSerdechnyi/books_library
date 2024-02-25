from django.db.models import Q, QuerySet
from django.utils.text import slugify

from src.utils.orm import parse_int_or_none


def search_books(queryset: QuerySet, query: str | None) -> QuerySet:
    if query:
        query = slugify(query.strip())
        multi_q = Q(
            Q(slug__icontains=query) |
            Q(authors__slug__icontains=query) |
            Q(genre__slug__icontains=query) |
            Q(year_of_publication__exact=parse_int_or_none(query))
        )
        queryset = queryset.filter(multi_q)
    return queryset


def sort_books(queryset: QuerySet, sort_by) -> QuerySet:
    match sort_by:
        case 'latest':
            queryset = queryset.order_by('-id')
        case 'title':
            queryset = queryset.order_by('title')
        case 'year_of_publication':
            queryset = queryset.order_by('year_of_publication')
        case _:
            queryset = queryset.order_by('-id')
    return queryset


def books_dependency_query(queryset: QuerySet) -> QuerySet:
    return queryset.prefetch_related('authors', 'genre').distinct()
