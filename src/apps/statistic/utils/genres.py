from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from plotly import express as px

from apps.library.models import Genre
from apps.statistic.forms import YearFilterForm


def get_years_from_request(request: HttpRequest) -> (int, int):
    form = YearFilterForm(request.GET)
    if not form.is_valid():
        all_errors = form.errors.get('__all__', [])
        error_messages = [str(error) for error in all_errors]
        raise ValidationError(error_messages)
    start_year = form.cleaned_data['start_year']
    end_year = form.cleaned_data['end_year']
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
    try:
        start_year, end_year = get_years_from_request(request)
    except ValidationError as e:
        return render(request, template_name, {'form': YearFilterForm(request.GET)})

    book_filter = filter_books_by_year(start_year, end_year)
    genre_count_dict = get_genre_statistics(book_filter)

    fig = px.pie(names=list(genre_count_dict.keys()), values=list(genre_count_dict.values()))
    fig.update_layout(title='Genre statistic')
    plotly_html = fig.to_html()

    context = {
        'form': YearFilterForm(request.GET),
        'fig': plotly_html,
    }

    return render(request, template_name, context)
