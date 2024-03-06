import plotly.express as px

from django.db.models import Q, Count, Avg
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.library.models import Genre, Author, Book, UserBookInstance
from utils.utils import get_minimal_book_year, get_maximal_book_year

DESC_LIMIT = 5


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


def get_authors_with_books_coun():
    return Author.objects.annotate(
        book_count=Count('books')
    ).values('full_name', 'book_count').order_by('-book_count')


def render_author_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    authors_with_books_count = get_authors_with_books_coun()
    author_count_dict = {item['full_name']: item['book_count'] for item in authors_with_books_count}
    fig = px.pie(names=list(author_count_dict.keys()), values=list(author_count_dict.values()))
    plotly_html = fig.to_html()
    context = {'fig': plotly_html}
    return render(request, template_name, context)


def get_user_books(user):
    return UserBookInstance.objects.filter(user=user)


def get_user_books_count(user):
    return get_user_books(user).count()


def get_read_books_count(user):
    return get_user_books(user).filter(is_read=True).count()


def get_total_books_count():
    return Book.objects.count()


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


def get_average_age_of_books():
    return Book.objects.aggregate(avg_age=Avg('year_of_publication'))['avg_age']


def get_popular_genres(limit=DESC_LIMIT):
    popular_genres = UserBookInstance.objects.values('book__genre__name').annotate(
        genre_count=Count('book__genre__name')).order_by('-genre_count')[:limit]
    return popular_genres


def get_popular_authors(limit=DESC_LIMIT):
    return UserBookInstance.objects.values('book__authors__full_name').annotate(
        author_count=Count('book__authors__full_name')).order_by('-author_count')[:limit]


def get_most_read_books(limit=DESC_LIMIT):
    return UserBookInstance.objects.filter(is_read=True).values('book__title', 'book__id').annotate(
        read_count=Count('book__id')).order_by('-read_count')[:limit]


def render_general_statistic_view(request: HttpRequest, template_name: str) -> HttpResponse:
    total_books = get_total_books_count()
    average_age = get_average_age_of_books()
    popular_genres = get_popular_genres()
    popular_authors = get_popular_authors()
    most_read_books = get_most_read_books()

    genre_labels = [item['book__genre__name'] for item in popular_genres]
    genre_counts = [item['genre_count'] for item in popular_genres]

    author_labels = [item['book__authors__full_name'] for item in popular_authors]
    author_counts = [item['author_count'] for item in popular_authors]

    most_read_books_labels = [item['book__title'] for item in most_read_books]
    most_read_books_counts = [item['read_count'] for item in most_read_books]

    fig_genre = px.bar(x=genre_labels, y=genre_counts, labels={'x': 'Genre', 'y': 'Count'},
                       title='Most Popular Genres')
    fig_author = px.bar(x=author_labels, y=author_counts, labels={'x': 'Author', 'y': 'Count'},
                        title='Most Popular Authors')
    fig_most_read_books = px.bar(x=most_read_books_labels, y=most_read_books_counts,
                                 labels={'x': 'Book', 'y': 'Read Count'},
                                 title='Most Read Books')

    plot_div_genre = fig_genre.to_html()
    plot_div_author = fig_author.to_html()
    plot_div_books = fig_most_read_books.to_html()

    context = {
        'total_books': total_books,
        'average_age': average_age,
        'most_read_books': most_read_books,
        'plot_div_genre': plot_div_genre,
        'plot_div_author': plot_div_author,
        'plot_div_books': plot_div_books,
    }
    return render(request, template_name, context)
