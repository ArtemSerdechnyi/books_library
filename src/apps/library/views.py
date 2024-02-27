from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView, ListView, DetailView

from .forms import BookForm
from .models import Book, UserBookInstance
from .utils import SearchBookMixin


def home_page_view(request: WSGIRequest):
    return render(request, 'library/index.html')


def add_book_to_user_library(request: WSGIRequest, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            book = get_object_or_404(Book, id=id)
            UserBookInstance.objects.create(book=book, user=request.user)
    return render(request, 'library/index.html')


class BookView(DetailView):
    model = Book
    template_name = 'library/book.html'
    context_object_name = 'book'


class LibrarySearch(SearchBookMixin, ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.search_book(queryset)
        return queryset


class Library(SearchBookMixin, ListView):
    model = Book
    template_name = 'library/library.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.search_book(queryset)
        if self.request.user.is_authenticated:
            user_books = self.request.user.books.all()
        return queryset


class UserLibrary(LoginRequiredMixin, ListView):
    model = UserBookInstance
    template_name = 'library/user_library.html'
    context_object_name = 'user_books'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_books = self.request.user.books.all()
        return user_books.all()


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
