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
        self.factory = RequestFactory()
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

    def test_book_view(self):
        url = reverse('library:book', kwargs={'slug': self.book.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        self.assertEqual(response.context_data['book'], self.book)
        self.assertNotIn('user_book_instance', response.context_data)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        self.assertEqual(response.context_data['book'], self.book)
        self.assertIn('user_book_instance', response.context_data)
        self.assertFalse(UserBookInstance.objects.filter(user=self.user, book=self.book).exists())
        self.assertIsNone(response.context_data['user_book_instance'])
        UserBookInstance.objects.create(user=self.user, book=self.book)
        self.assertTrue(UserBookInstance.objects.filter(user=self.user, book=self.book).exists())
        response = self.client.get(url)
        self.assertEqual(response.context_data['user_book_instance'].book, self.book)

        wrong_slug = 'wrong-slug'
        self.assertFalse(Book.objects.filter(slug=wrong_slug).exists())
        url = reverse('library:book', kwargs={'slug': wrong_slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_library_view(self):
        url = reverse('library:library')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context_data['books']), set(Book.objects.all()))

        # test for search bar, 'q' attribute
        response = self.client.get(reverse('library:library') + '?q=New+Book')
        self.assertEqual(
            set(response.context_data['books']),
            set(Book.objects.filter(title__icontains='New Book'))
        )
        response = self.client.get(reverse('library:library') + '?q=2000')
        self.assertEqual(
            set(response.context_data['books']),
            set(Book.objects.filter(year_of_publication=2000))
        )

        create_book(title='Second New Book')

        response = self.client.get(reverse('library:library') + '?q=2000')
        self.assertEqual(
            set(response.context_data['books']),
            set(Book.objects.filter(year_of_publication=2000))
        )
        response = self.client.get(reverse('library:library') + '?q=Author+First+Name+1+Author+Last+Name+1')
        self.assertEqual(
            set(response.context_data['books']),
            set(Book.objects.filter(authors__full_name__icontains='Author First Name 1 Author Last Name 1'))
        )
        response = self.client.get(reverse('library:library') + '?q=Genre+Name+1')
        self.assertEqual(
            set(response.context_data['books']),
            set(Book.objects.filter(genre__name__icontains='Genre Name 1'))
        )
        create_book(title='A New Book')
        # test for sorting, 'sorted' attribute
        response = self.client.get(reverse('library:library') + '?q=&sorted=title')
        self.assertNotEqual(
            list(response.context_data['books']),
            list(Book.objects.all())
        )
        self.assertEqual(
            list(response.context_data['books']),
            list(Book.objects.all().order_by('title'))
        )
        response = self.client.get(reverse('library:library') + '?q=&sorted=year_of_publication')
        self.assertNotEqual(
            list(response.context_data['books']),
            list(Book.objects.all())
        )
        self.assertEqual(
            list(response.context_data['books']),
            list(Book.objects.all().order_by('year_of_publication'))
        )

        print(response.context_data)
        response = self.client.get(reverse('library:library') + '?q=Second+New+Book')
        with self.assertRaises(AttributeError):
            self.assertTrue((response.context_data['books'].first()).read)
        self.client.force_login(self.user)
        UserBookInstance.objects.create(user=self.user, book=Book.objects.get(title='Second New Book'), is_read=True)
        response = self.client.get(reverse('library:library') + '?q=Second+New+Book')
        self.assertTrue((response.context_data['books'].first()).read)

        # self.client.force_login(self.user)
        # response = self.client.get(url)
        # self.assertEqual(response.status_code, 200)
        # self.assertContains(response, self.book.title)
        # self.assertEqual(response.context_data['book'], self.book)
        # self.assertIn('user_book_instance', response.context_data)
        # self.assertFalse(UserBookInstance.objects.filter(user=self.user, book=self.book).exists())
        # self.assertIsNone(response.context_data['user_book_instance'])
        # UserBookInstance.objects.create(user=self.user, book=self.book)

    # def test_library_view(self):
    #     request = self.factory.get(reverse('library:library'))
    #     # request.user = self.user
    #     self.client.login(username='testuser', password='test')
    #     response = views.Library.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_library_search_view(self):
    #     request = self.factory.get(reverse('library:library_search'))
    #     response = views.LibrarySearch.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_user_library_view(self):
    #     request = self.factory.get(reverse('library:user_books'))
    #     request.user = self.user
    #     response = views.UserLibrary.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_user_library_filter_view(self):
    #     request = self.factory.get(reverse('library:user_books_filter'))
    #     request.user = self.user
    #     response = views.UserLibraryFilter.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
    # #
    # def test_add_book_view(self):
    #     request = self.factory.post(reverse('library:add_book'), data={'title': 'Test Book'})
    #     request.user = self.user
    #     response = views.AddBook.as_view()(request)
    #     self.assertEqual(response.status_code, 302)  # Expecting redirect on successful form submission
