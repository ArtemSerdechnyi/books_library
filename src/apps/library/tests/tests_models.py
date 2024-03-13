import os

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.conf import settings

from apps.library.models import Country, Author, Genre, Book, UserBookInstance
from utils.tests.utils import get_mock_file, create_book_in_db


class ModelTestCase(TestCase):
    fixtures = ['test_data.json']

    def tearDown(self):
        # called for remove created files
        books = Book.objects.all()
        for book in books:
            book.delete()

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
        create_book_in_db(year_of_publication=0, image=get_mock_file('test_image.png', 1))
        book = Book.objects.get(title='New Book Title')
        self.assertEqual(book.title, 'New Book Title')
        self.assertEqual(book.slug, 'new-book-title')
        # self.assertEqual(book.image, 'default_book_image.jpg')
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

        # check load and delete logic for image and file fields
        book = Book.objects.get(title='New Book Title')
        media_root = settings.MEDIA_ROOT
        image_path = os.path.join(media_root, book.image.name)
        self.assertTrue(os.path.exists(image_path))
        book_file_path = os.path.join(media_root, book.file.name)
        self.assertTrue(os.path.exists(book_file_path))
        book.delete()
        self.assertFalse(os.path.exists(image_path))
        self.assertFalse(os.path.exists(book_file_path))


    def test_invalid_book_model(self):
        with self.assertRaises(ValidationError):
            create_book_in_db(title='Unique test book')
            create_book_in_db(title='Unique test book')

        with self.assertRaises(ValidationError):
            create_book_in_db(title='Min year error', year_of_publication=-1001)

        with self.assertRaises(ValidationError):
            create_book_in_db(title='Max year error', year_of_publication=timezone.now().year + 1)

        with self.assertRaises(ValidationError):
            create_book_in_db(title='Max book file size error',
                              file=get_mock_file('max_size_error.txt', 31))

        with self.assertRaises(ValidationError):
            create_book_in_db(title='Max book image size error',
                              image=get_mock_file('max_size_error.jpg', 6))

    def test_user_book_instance_model(self):
        create_book_in_db(title='New Book')
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
