from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.library.models import Book
from apps.library.forms import BookForm


class FormTestCase(TestCase):
    fixtures = ['test_data.json']

    def tearDown(self):
        # called for remove created files
        books = Book.objects.all()
        for book in books:
            book.delete()

    def test_book_form_valid(self):
        data = {
            'title': 'TestForm',
            'description': 'description',
            'authors': [1, 2],
            'genre': [1],
            'year_of_publication': 2000,
        }

        file = SimpleUploadedFile("testfile.pdf", b'Test file content', content_type="application/pdf")
        form = BookForm(data=data, files={'file': file})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Book.objects.filter(title='TestForm').exists())

    def test_book_form_invalid(self):
        data = {
            'title': 'TestForm',
            'description': 'description',
            'authors': [1, 2],
            'genre': [1],
            'year_of_publication': 2000,
        }

        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertFalse(Book.objects.filter(title='TestForm').exists())
