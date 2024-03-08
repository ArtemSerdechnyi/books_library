from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render

from .forms import YearFilterForm
from .utils import (
    render_genre_statistic_view,
    render_author_statistic_view,
    render_read_book_statistic_view,
    render_general_statistic_view,
)


@login_required
def statistic_page_view(request: WSGIRequest):
    return render(request, 'statistic/statistic.html')


@login_required
def genres_statistic_view(request: WSGIRequest):
    return render_genre_statistic_view(request, 'statistic/genres_statistic.html')


@login_required
def fig_genres_statistic_view(request: WSGIRequest):
    return render_genre_statistic_view(request, 'statistic/fig_genres_statistic.html')


@login_required
def authors_statistic_view(request: WSGIRequest):
    return render_author_statistic_view(request, 'statistic/authors_statistic.html')


@login_required
def books_read_statistics_view(request: WSGIRequest):
    return render_read_book_statistic_view(request, 'statistic/books_read_statistic.html')


@login_required
def general_statistics_view(request):
    return render_general_statistic_view(request, 'statistic/general_statistics.html')
