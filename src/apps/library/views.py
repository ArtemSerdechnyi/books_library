from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import FormView, ListView, DetailView

from .forms import BookForm
from .models import Book, UserBookInstance
from .utils.views_utils import (
    SearchBookMixin,
    UserBookFilterMixin,
    create_book_instance, get_book_instance,
)


def home_page_view(request: WSGIRequest):
    return render(request, 'library/index.html')


@require_POST
@login_required
def add_book_to_user_library_view(request: WSGIRequest, id):
    """
    Add a book to the user's library.
    """
    book = get_object_or_404(Book, id=id)
    create_book_instance(book, request.user)
    return redirect('library:book', slug=book.slug)


@require_POST
@login_required
def remove_book_from_user_library_view(request: WSGIRequest, id):
    """
    Remove a book from the user library.
    """
    book = get_object_or_404(Book, id=id)
    user_book_instance = get_book_instance(book, request.user)
    user_book_instance.delete()
    return redirect('library:book', slug=book.slug)


@require_POST
@login_required
def change_book_read_status_view(request: WSGIRequest, id):
    """
    Change the read status of a book in the user's library.
    """
    book = get_object_or_404(Book, id=id)
    user_book_instance = get_book_instance(book, request.user)
    user_book_instance.is_read = not user_book_instance.is_read
    user_book_instance.save()
    return HttpResponse(status=200)


class BookView(DetailView):
    """
    View for displaying details of a book, in the book page.
    """
    model = Book
    template_name = 'library/book.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            book = context.get('book')
            user_book_instance = UserBookInstance.objects.filter(user=user, book=book).first()
            context['user_book_instance'] = user_book_instance
        return context


class LibraryView(SearchBookMixin, ListView):
    """
    View for displaying a list of existing books on the library page,
    implementing search and sorting functionality, base on request query.
    """
    model = Book
    template_name = 'library/library.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.search_book(queryset)
        return queryset


class LibrarySearchView(LibraryView):
    """
    View for displaying only list of existing books, base on request query.
    """
    template_name = 'library/book_list.html'


class UserLibraryView(LoginRequiredMixin, UserBookFilterMixin, ListView):
    """
    View for displaying list books in user library, full page. Implementing filtering functionality.
    """
    model = UserBookInstance
    template_name = 'library/user_library.html'
    context_object_name = 'user_books'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('book')
        queryset = self.user_book_filter(queryset)
        return queryset


class UserLibraryFilterView(UserLibraryView):
    """
    View for displaying only list books in user library. Implementing filtering functionality.
    """
    template_name = 'library/user_book_list.html'


class AddBookView(LoginRequiredMixin, FormView):
    """
    View for adding a book to db.
    """
    template_name = 'library/add_book.html'
    form_class = BookForm
    success_url = reverse_lazy('account:user_account')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
