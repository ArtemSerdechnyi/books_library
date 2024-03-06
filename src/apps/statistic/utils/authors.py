from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from plotly import express as px

from apps.library.models import Author


def get_authors_with_books_count():
    return Author.objects.annotate(
        book_count=Count('books')
    ).values('full_name', 'book_count').order_by('-book_count')


def render_author_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    authors_with_books_count = get_authors_with_books_count()
    author_count_dict = {item['full_name']: item['book_count'] for item in authors_with_books_count}
    fig = px.pie(names=list(author_count_dict.keys()), values=list(author_count_dict.values()))
    plotly_html = fig.to_html()
    context = {'fig': plotly_html}
    return render(request, template_name, context)
