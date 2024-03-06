from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from plotly import express as px

from apps.library.models import Book, UserBookInstance
from .generic import get_total_books_count

DESC_LIMIT = 5


def get_average_age_of_books():
    return Book.objects.aggregate(avg_age=Avg('year_of_publication'))['avg_age']


def get_popular_genres(limit=DESC_LIMIT):
    popular_genres = UserBookInstance.objects.values('book__genre__name').annotate(
        genre_count=Count('book__genre__name')).order_by('-genre_count')[:limit]
    return popular_genres


def get_popular_authors(limit=DESC_LIMIT):
    return UserBookInstance.objects.values('book__authors__full_name').annotate(
        author_count=Count('book__authors__full_name')).order_by('-author_count')[:limit]


def get_most_read_books(limit=DESC_LIMIT):
    return UserBookInstance.objects.filter(is_read=True).values('book__title', 'book__id').annotate(
        read_count=Count('book__id')).order_by('-read_count')[:limit]


def render_general_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    total_books = get_total_books_count()
    average_age = get_average_age_of_books()
    popular_genres = get_popular_genres()
    popular_authors = get_popular_authors()
    most_read_books = get_most_read_books()

    genre_labels = [item['book__genre__name'] for item in popular_genres]
    genre_counts = [item['genre_count'] for item in popular_genres]

    author_labels = [item['book__authors__full_name'] for item in popular_authors]
    author_counts = [item['author_count'] for item in popular_authors]

    most_read_books_labels = [item['book__title'] for item in most_read_books]
    most_read_books_counts = [item['read_count'] for item in most_read_books]

    fig_genre = px.bar(x=genre_labels, y=genre_counts, labels={'x': 'Genre', 'y': 'Count'},
                       title='Most Popular Genres')
    fig_author = px.bar(x=author_labels, y=author_counts, labels={'x': 'Author', 'y': 'Count'},
                        title='Most Popular Authors')
    fig_most_read_books = px.bar(x=most_read_books_labels, y=most_read_books_counts,
                                 labels={'x': 'Book', 'y': 'Read Count'},
                                 title='Most Read Books')

    plot_div_genre = fig_genre.to_html()
    plot_div_author = fig_author.to_html()
    plot_div_books = fig_most_read_books.to_html()

    context = {
        'total_books': total_books,
        'average_age': average_age,
        'most_read_books': most_read_books,
        'plot_div_genre': plot_div_genre,
        'plot_div_author': plot_div_author,
        'plot_div_books': plot_div_books,
    }
    return render(request, template_name, context)
