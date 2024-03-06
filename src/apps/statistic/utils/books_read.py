from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from plotly import express as px

from apps.library.models import UserBookInstance
from .generic import get_total_books_count


def get_user_books(user):
    return UserBookInstance.objects.filter(user=user)


def get_user_books_count(user):
    return get_user_books(user).count()


def get_read_books_count(user):
    return get_user_books(user).filter(is_read=True).count()


def render_read_book_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    user = request.user
    book_instances_count = get_user_books_count(user)
    read_book_instances_count = get_read_books_count(user)
    total_books = get_total_books_count()

    data = {'Status': ['Total Books', 'Books in my library', 'Read Books'],
            'Count': [total_books, book_instances_count, read_book_instances_count]}

    fig = px.bar(data, x='Count', y='Status', orientation='h')
    plotly_html = fig.to_html()
    context = {'fig': plotly_html}
    return render(request, template_name, context)
