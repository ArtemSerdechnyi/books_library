from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile, SimpleUploadedFile

from apps.library.models import Book, Genre, Author


def get_mock_file(
        name,
        size_in_mb,
):
    full_size = size_in_mb * 1024 * 1024

    return InMemoryUploadedFile(
        file=BytesIO(b'test content'),
        field_name=None,
        name=name,
        content_type='text/plain',
        size=full_size,
        charset=None,
        content_type_extra=None,
    )


def create_book_in_db(
        title='New Book Title',
        year_of_publication=2000,
        file=get_mock_file('new_book_file.txt', 10),
        added_by=None,
        **kwargs,
) -> None:
    book_data = {
        'title': title,
        'year_of_publication': year_of_publication,
        'file': file,
        'added_by': added_by,
    }

    if kwargs:
        book_data.update(kwargs)

    test_book = Book(**book_data)
    test_book.save()
    test_book.genre.set([Genre.objects.get(name='Genre Name 1'),
                         Genre.objects.get(name='Genre Name 2')])
    test_book.authors.set([Author.objects.get(first_name='Author First Name 1'),
                           Author.objects.get(first_name='Author First Name 2')])
