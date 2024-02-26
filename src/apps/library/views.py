from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.views.generic import FormView, ListView, DetailView

from src.utils.orm import parse_int_or_none
from .forms import BookForm
from .models import Book, Author, Genre
from .utils import search_books, sort_books, books_dependency_query


def home_page_view(request: WSGIRequest):
    return render(request, 'library/index.html')


class BookView(DetailView):
    model = Book
    template_name = 'library/book.html'
    context_object_name = 'book'


class Library(ListView):
    model = Book
    template_name = 'library/library.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        get_q = self.request.GET.get('q')
        get_sorted = self.request.GET.get('sorted')
        queryset = search_books(queryset, get_q)
        queryset = sort_books(queryset, get_sorted)
        queryset = books_dependency_query(queryset)
        return queryset


class AddBook(FormView):
    template_name = 'library/add_book.html'
    form_class = BookForm
    success_url = '/'

    def form_valid(self, form):
        # Override to handle saving authors not found in the existing list
        authors = form.cleaned_data['authors']
        for author in authors:
            if not author.pk:
                author.save()
        return super().form_valid(form)


def library_search_view(request: WSGIRequest):
    get_q = request.GET.get('q')
    get_sorted = request.GET.get('sorted')
    queryset = Book.objects.all()
    queryset = search_books(queryset, get_q)
    queryset = sort_books(queryset, get_sorted)
    queryset = books_dependency_query(queryset)

    return render(request, 'library/book_list.html', {'books': queryset})
