from apps.library.models import Book


def get_total_books_count():
    return Book.objects.count()
