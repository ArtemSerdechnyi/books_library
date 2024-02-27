from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic import FormView, ListView, DetailView

from .forms import BookForm
from .models import Book
from .utils import SearchBookMixin


def home_page_view(request: WSGIRequest):
    return render(request, 'library/index.html')


class BookView(DetailView):
    model = Book
    template_name = 'library/book.html'
    context_object_name = 'book'


class Library(SearchBookMixin, ListView):
    model = Book
    template_name = 'library/library.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.search_book(queryset)
        return queryset


class LibrarySearch(SearchBookMixin, ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.search_book(queryset)
        return queryset


class AddBook(FormView):
    template_name = 'library/add_book.html'
    form_class = BookForm
    success_url = '/'

    def form_valid(self, form):
        authors = form.cleaned_data['authors']
        for author in authors:
            if not author.pk:
                author.save()
        return super().form_valid(form)
