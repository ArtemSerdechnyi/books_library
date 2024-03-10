from io import BytesIO

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase

from apps.library.models import Country, Author, Genre, Book, UserBookInstance


class ModelTestCase(TestCase):
    fixtures = ['test_data.json']

    @staticmethod
    def get_mock_file(
            name,
            size_in_mb,
    ) -> InMemoryUploadedFile:
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

    @staticmethod
    def create_book(
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

    def test_country_model(self):
        country = Country.objects.create(name='New Country')
        self.assertEqual(country.name, 'New Country')
        self.assertEqual(country.slug, 'new-country')
        self.assertIn(country, Country.objects.all())

        country = Country.objects.get(name='Country Name 1')
        self.assertEqual(country.name, 'Country Name 1')
        self.assertEqual(country.slug, 'country-name-1')

    def test_author_model(self):
        author = Author.objects.create(
            first_name='New Author First Name',
            last_name='New Author Last Name',
            country=Country.objects.get(name='Country Name 1'),
        )
        self.assertEqual(author.first_name, 'New Author First Name')
        self.assertEqual(author.last_name, 'New Author Last Name')
        self.assertEqual(author.full_name, 'New Author First Name New Author Last Name')
        self.assertEqual(author.slug, 'new-author-first-name-new-author-last-name')
        self.assertIn(author, Author.objects.all())

        author = Author.objects.get(first_name='Author First Name 1', last_name='Author Last Name 1')
        self.assertEqual(author.first_name, 'Author First Name 1')
        self.assertEqual(author.last_name, 'Author Last Name 1')
        self.assertEqual(author.full_name, 'Author First Name 1 Author Last Name 1')
        self.assertEqual(author.slug, 'author-first-name-1-author-last-name-1')
        self.assertEqual(author.country.name, 'Country Name 1')

    def test_genre_model(self):
        genre = Genre.objects.create(name='New Genre')
        self.assertEqual(genre.name, 'New Genre')
        self.assertEqual(genre.slug, 'new-genre')
        self.assertIn(genre, Genre.objects.all())

        genre = Genre.objects.get(name='Genre Name 1')
        self.assertEqual(genre.name, 'Genre Name 1')
        self.assertEqual(genre.slug, 'genre-name-1')

    def test_book_model(self):
        self.create_book(year_of_publication=0)
        book = Book.objects.get(title='New Book Title')
        self.assertEqual(book.title, 'New Book Title')
        self.assertEqual(book.slug, 'new-book-title')
        self.assertEqual(book.image, 'default_book_image.jpg')
        self.assertEqual(book.year_of_publication, 0)
        self.assertIsNone(book.added_by)
        self.assertIn(book, Book.objects.all())

        book = Book.objects.get(title='Book Title 1')
        self.assertEqual(book.title, 'Book Title 1')
        self.assertEqual(book.slug, 'book-title-1')
        self.assertEqual(book.year_of_publication, 2022)
        self.assertEqual(book.added_by_id, 1)

        author = Author.objects.get(first_name='Author First Name 1', last_name='Author Last Name 1')
        genre = Genre.objects.get(name='Genre Name 1')
        self.assertIn(author, book.authors.all())
        self.assertIn(genre, book.genre.all())

    def test_invalid_book_model(self):
        with self.assertRaises(ValidationError):
            self.create_book(title='Unique test book')
            self.create_book(title='Unique test book')

        with self.assertRaises(ValidationError):
            self.create_book(title='Min year error', year_of_publication=-1001)

        with self.assertRaises(ValidationError):
            self.create_book(title='Max year error', year_of_publication=timezone.now().year + 1)

        with self.assertRaises(ValidationError):
            self.create_book(title='Max book file size error',
                             file=self.get_mock_file('max_size_error.txt', 31))

        with self.assertRaises(ValidationError):
            self.create_book(title='Max book image size error',
                             image=self.get_mock_file('max_size_error.jpg', 6))

    def test_user_book_instance_model(self):
        self.create_book(title='New Book')
        book = Book.objects.get(title='New Book')
        instance = UserBookInstance.objects.create(user_id=1, book=book, is_read=True)
        self.assertEqual(instance.user_id, 1)
        self.assertEqual(instance.book.title, 'New Book')
        self.assertEqual(instance.is_read, True)
        self.assertIn(instance, UserBookInstance.objects.all())

        instance = UserBookInstance.objects.get(book__title='Book Title 1')
        self.assertEqual(instance.user_id, 1)
        self.assertEqual(instance.book_id, 1)
        self.assertFalse(instance.is_read)

    def test_invalid_user_book_instance_model(self):
        with self.assertRaises(ValidationError):
            UserBookInstance.objects.create(user_id=1, book_id=1, is_read=True)
            UserBookInstance.objects.create(user_id=1, book_id=1, is_read=False)
