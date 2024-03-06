import plotly.express as px

from django.db.models import Q, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.library.models import Genre, Author, Book, UserBookInstance
from utils.utils import get_minimal_book_year, get_maximal_book_year


def get_years_from_request(request: HttpRequest) -> (int, int):
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


def render_genre_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    start_year, end_year = get_years_from_request(request)
    book_filter = filter_books_by_year(start_year, end_year)
    genre_count_dict = get_genre_statistics(book_filter)

    fig = px.pie(names=list(genre_count_dict.keys()), values=list(genre_count_dict.values()))
    fig.update_layout(title='Genre statistic')
    plotly_html = fig.to_html()
    context = {'fig': plotly_html}
    return render(request, template_name, context)


def render_author_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    authors_with_books_count = Author.objects.annotate(
        book_count=Count('books')
    ).values('full_name', 'book_count').order_by('-book_count')
    author_count_dict = {item['full_name']: item['book_count'] for item in authors_with_books_count}
    fig = px.pie(names=list(author_count_dict.keys()), values=list(author_count_dict.values()))
    plotly_html = fig.to_html()
    context = {'fig': plotly_html}
    return render(request, template_name, context)


def render_read_book_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    user = request.user
    user_book_instances = UserBookInstance.objects.filter(user=user)
    book_instances_count = user_book_instances.count()
    read_book_instances_count = user_book_instances.filter(is_read=True).count()
    total_books = Book.objects.count()

    data = {'Status': ['Total Books', 'Books in my library', 'Read Books'],
            'Count': [total_books, book_instances_count, read_book_instances_count]}

    fig = px.bar(data, x='Count', y='Status', orientation='h')
    plotly_html = fig.to_html()
    context = {'fig': plotly_html}
    return render(request, template_name, context)
