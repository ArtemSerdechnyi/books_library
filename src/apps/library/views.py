from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.views.generic import FormView, ListView, DetailView

from src.utils.orm import parse_int_or_none
from .forms import BookForm
from .models import Book, Author, Genre


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
        queryset = queryset.prefetch_related('authors', 'genre')
        get_query = self.request.GET.get('q')

        if get_query:
            get_query = slugify(get_query.strip())
            multy_q = Q(
                Q(slug__icontains=get_query) |
                Q(authors__slug__icontains=get_query) |
                Q(genre__slug__icontains=get_query) |
                Q(year_of_publication__exact=parse_int_or_none(get_query))
            )
            queryset = queryset.filter(multy_q)
        return queryset.distinct()


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
    get_query = request.GET.get('q')
    get_sorted = request.GET.get('sorted')

    if get_query:
        get_query = slugify(get_query.strip())
        multy_q = Q(
            Q(slug__icontains=get_query) |
            Q(authors__slug__icontains=get_query) |
            Q(genre__slug__icontains=get_query) |
            Q(year_of_publication__exact=parse_int_or_none(get_query))
        )
        books = Book.objects.filter(multy_q).distinct()
    else:
        books = Book.objects.all()

    match get_sorted:
        case 'latest':
            books = books.order_by('-id')
        case'title':
            books = books.order_by('title')
        case 'year_of_publication':
            books = books.order_by('year_of_publication')
        case _:
            books = books.order_by('id')

    books = books.prefetch_related('authors', 'genre')
    return render(request, 'library/search.html', {'books': books})
