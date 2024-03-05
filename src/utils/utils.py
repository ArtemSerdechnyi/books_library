from django.utils import timezone


def get_minimal_book_year():
    return -1000


def get_maximal_book_year():
    return timezone.now().year
