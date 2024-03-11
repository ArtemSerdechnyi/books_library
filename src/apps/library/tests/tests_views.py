from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.library.models import Book, UserBookInstance
from apps.library import views
from utils.tests.utils import create_book


class TestViews(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        create_book(title='New Book')
        self.book = Book.objects.get(title='New Book')
        self.user = get_user_model().objects.get(id=1)

    def test_add_book_to_user_library(self):
        url = reverse('library:add_book_to_user_library', args=[self.book.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserBookInstance.objects.filter(user=self.user, book=self.book).exists())

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(UserBookInstance.objects.filter(user=self.user, book=self.book).exists())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserBookInstance.objects.filter(user=self.user, book=self.book).exists())
        with self.assertRaises(ValidationError):
            self.client.post(url)

        wrong_book_id = 1000
        url = reverse('library:add_book_to_user_library', args=[wrong_book_id])
        self.assertFalse(UserBookInstance.objects.filter(id=wrong_book_id).exists())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_remove_book_from_user_library(self):
        url = reverse('library:remove_book_from_user_library', args=[self.book.id])
        user_book_instance = UserBookInstance.objects.create(user=self.user, book=self.book)
        self.assertTrue(UserBookInstance.objects.filter(id=user_book_instance.id).exists())

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserBookInstance.objects.filter(id=user_book_instance.id).exists())

        self.client.force_login(self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(UserBookInstance.objects.filter(id=user_book_instance.id).exists())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserBookInstance.objects.filter(id=user_book_instance.id).exists())

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(UserBookInstance.objects.filter(id=user_book_instance.id).exists())

        wrong_book_id = 1000
        url = reverse('library:remove_book_from_user_library', args=[wrong_book_id])
        self.assertFalse(UserBookInstance.objects.filter(id=wrong_book_id).exists())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_change_book_read_status(self):
        url = reverse('library:change_book_read_status', args=[self.book.id])
        user_book_instance = UserBookInstance.objects.create(user=self.user, book=self.book)
        self.assertFalse(UserBookInstance.objects.get(id=user_book_instance.id).is_read)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserBookInstance.objects.get(id=user_book_instance.id).is_read)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(UserBookInstance.objects.get(id=user_book_instance.id).is_read)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserBookInstance.objects.get(id=user_book_instance.id).is_read)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserBookInstance.objects.get(id=user_book_instance.id).is_read)

        wrong_book_id = 1000
        url = reverse('library:change_book_read_status', args=[wrong_book_id])
        self.assertFalse(UserBookInstance.objects.filter(id=wrong_book_id).exists())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
