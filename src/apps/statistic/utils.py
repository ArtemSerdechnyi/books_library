import plotly.express as px

from django.db.models import Q, Count
from django.http import HttpRequest
from django.shortcuts import render

from apps.library.models import Genre
from utils.utils import get_minimal_book_year, get_maximal_book_year


def get_years(request: HttpRequest) -> (int, int):
    start_year_str = request.GET.get('start_year')
    end_year_str = request.GET.get('end_year')

    start_year = int(start_year_str) if start_year_str else get_minimal_book_year()
    end_year = int(end_year_str) if end_year_str else get_maximal_book_year()

    return start_year, end_year


def filter_books_by_year(start_year: int, end_year: int) -> Q:
    book_filter = Q()
    if start_year:
        book_filter &= Q(books__year_of_publication__gte=start_year)
    if end_year:
        book_filter &= Q(books__year_of_publication__lte=end_year)

    return book_filter


def get_genre_statistics(book_filter: Q) -> dict[str, int]:
    genre_counts = Genre.objects.annotate(
        book_count=Count('books', filter=book_filter)
    ).values('name', 'book_count').order_by('-book_count')

    return {item['name']: item['book_count'] for item in genre_counts}


def render_genre_statistic_view(request: HttpRequest, template_name: str) -> render:
    start_year, end_year = get_years(request)
    book_filter = filter_books_by_year(start_year, end_year)
    genre_count_dict = get_genre_statistics(book_filter)

    fig = px.pie(names=list(genre_count_dict.keys()), values=list(genre_count_dict.values()))
    fig.update_layout(title='Genre statistic')
    plotly_html = fig.to_html()
    context = {'fig': plotly_html}
    return render(request, template_name, context)
