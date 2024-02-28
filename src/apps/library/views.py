from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import FormView, ListView, DetailView

from .forms import BookForm
from .models import Book, UserBookInstance
from .utils import SearchBookMixin


def home_page_view(request: WSGIRequest):
    return render(request, 'library/index.html')


@require_POST
def add_book_to_user_library(request: WSGIRequest, id):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, id=id)
        UserBookInstance.objects.create(book=book, user=request.user)
        return redirect('library:book', slug=book.slug)
    return HttpResponseNotFound()


@require_POST
def remove_book_from_user_library(request: WSGIRequest, id):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, id=id)
        user_book_instance = UserBookInstance.objects.filter(user=request.user, book=book).first()
        user_book_instance.delete()
        return redirect('library:book', slug=book.slug)
    return HttpResponseNotFound()


class BookView(DetailView):
    model = Book
    template_name = 'library/book.html'
    context_object_name = 'book'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if user := self.request.user:
            book = context.get('book')
            user_book_instance = UserBookInstance.objects.filter(user=user, book=book).first()
            context['user_book_instance'] = user_book_instance
        return context


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
