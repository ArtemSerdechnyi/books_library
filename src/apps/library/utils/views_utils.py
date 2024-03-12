from django.core.exceptions import BadRequest
from django.db.models import QuerySet, Case, When, BooleanField, Q
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from utils.orm import parse_int_or_none
from ..models import UserBookInstance


def create_book_instance(book, user) -> None:
    UserBookInstance.objects.create(book=book, user=user)


def get_book_instance(book, user) -> UserBookInstance:
    return get_object_or_404(UserBookInstance, user=user, book=book)


def annotate_books_with_read_flag(queryset, user) -> QuerySet:
    if user.is_authenticated:
        id_read_books = user.books.filter(is_read=True).values_list('book_id', flat=True)
        queryset = queryset.annotate(
            read=Case(
                When(pk__in=id_read_books, then=True),
                default=False,
                output_field=BooleanField()
            )
        )
    return queryset


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
        case 'read':
            queryset = queryset.order_by('-read')
        case _:
            queryset = queryset.order_by('-id')
    return queryset


def books_dependency_query(queryset: QuerySet) -> QuerySet:
    return queryset.prefetch_related('authors', 'genre').distinct()


class UserBookFilterMixin:
    def user_book_filter(self, queryset: QuerySet) -> QuerySet:
        queryset = queryset.filter(user=self.request.user)
        book_filter = self.request.GET.get('filter')
        match book_filter:
            case 'read':
                queryset = queryset.filter(is_read=True)
            case 'unread':
                queryset = queryset.filter(is_read=False)
        return queryset


class SearchBookMixin:
    def search_book(self, queryset: QuerySet):
        get_q = self.request.GET.get('q')
        get_sorted = self.request.GET.get('sorted')
        if get_sorted == 'read' and not self.request.user.is_authenticated:
            raise BadRequest("Authentication required")

        queryset = annotate_books_with_read_flag(queryset, self.request.user)
        queryset = search_books(queryset, get_q)
        queryset = sort_books(queryset, get_sorted)
        queryset = books_dependency_query(queryset)
        return queryset
