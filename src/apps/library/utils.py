from pathlib import Path

from django.conf import settings


def get_book_path(instance, filename) -> str:
    return settings.BOOKS_PATH / filename
