from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.template.response import TemplateResponse
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.library.models import Book, UserBookInstance
from utils.tests.utils import create_book_in_db, get_mock_file


class TestViews(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.factory = RequestFactory()
        create_book_in_db(title='New Book')
        self.book = Book.objects.get(title='New Book')
        self.user = get_user_model().objects.get(id=1)

    def tearDown(self):
        # called for remove created files
        books = Book.objects.all()
        for book in books:
            book.delete()

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
        def q_attribute_checker(url: str, equal_query: QuerySet):
            """
            Helper function to check if the response data matches the expected
            queryset based on the 'q' attribute in the URL.
            """
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                set(response.context_data['books']),
                set(equal_query)
            )

        def sorted_attribute_checker(url: str, equal_query: QuerySet):
            """
            Helper function to check if the response data is sorted
            correctly based on the 'sorted' attribute in the URL.
            """
            response = self.client.get(url)
            model = response.context_data['books'].model
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(
                list(response.context_data['books']),
                list(model.objects.all())
            )
            self.assertEqual(
                list(response.context_data['books']),
                list(equal_query)
            )

        create_book_in_db(title='A New Book', year_of_publication=0)
        create_book_in_db(title='Second New Book', year_of_publication=-200)
        create_book_in_db(title='Third New Book', year_of_publication=-200)
        UserBookInstance.objects.create(user=self.user, book=Book.objects.get(title='Second New Book'), is_read=True)

        url = reverse('library:library')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context_data['books']), set(Book.objects.all()))

        response = self.client.get(reverse('library:library') + '?q=Second+New+Book')
        with self.assertRaises(AttributeError):
            self.assertTrue((response.context_data['books'].first()).read)

        # tests for search bar, 'q' attribute
        q_attribute_checker(
            reverse('library:library') + '?q=New+Book',
            Book.objects.filter(title__icontains='New Book')
        )
        q_attribute_checker(
            reverse('library:library') + '?q=2000',
            Book.objects.filter(year_of_publication=2000)
        )
        q_attribute_checker(
            reverse('library:library') + '?q=Author+First+Name+1+Author+Last+Name+1',
            Book.objects.filter(authors__full_name__icontains='Author First Name 1 Author Last Name 1')
        )
        q_attribute_checker(
            reverse('library:library') + '?q=Genre+Name+1',
            Book.objects.filter(genre__name__icontains='Genre Name 1')
        )

        # tests for sorting, 'sorted' attribute
        sorted_attribute_checker(
            reverse('library:library') + '?q=&sorted=title',
            Book.objects.all().order_by('title')
        )
        sorted_attribute_checker(
            reverse('library:library') + '?q=&sorted=year_of_publication',
            Book.objects.all().order_by('year_of_publication')
        )
        sorted_attribute_checker(
            reverse('library:library') + '?q=&sorted=latest',
            Book.objects.all().order_by('-id')
        )
        response = self.client.get(reverse('library:library') + '?q=&sorted=read')
        self.assertEqual(response.status_code, 400)

        # tests with login user
        self.client.force_login(self.user)

        response = self.client.get(reverse('library:library') + '?q=Second+New+Book')
        self.assertTrue((response.context_data['books'].first()).read)

        UserBookInstance.objects.create(user=self.user, book=Book.objects.get(title='A New Book'), is_read=True)
        read_books = list(
            UserBookInstance.objects.filter(user=self.user, is_read=True)
            .values_list('book_id', flat=True).order_by('book_id'))
        books = list(Book.objects.all().values_list('id', flat=True))
        # move read_books to start of the list
        for i in read_books[::-1]:
            if i in books:
                books.remove(i)
                books.insert(0, i)

        response = self.client.get(reverse('library:library') + '?q=&sorted=read')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            list(response.context_data['books'].values_list('id', flat=True)),
            list(Book.objects.all().values_list('id', flat=True))
        )
        self.assertEqual(
            list(response.context_data['books'].values_list('id', flat=True)),
            books
        )

        # tests for both 'q' and 'sorted' attributes
        sorted_attribute_checker(
            reverse('library:library') + '?q=new&sorted=year_of_publication',
            Book.objects.filter(title__icontains='new').order_by('year_of_publication')
        )

    def test_library_search_view(self):
        url = reverse('library:library_search') + '?q=new&sorted=year_of_publication'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            list(response.context_data['books']),
            list(Book.objects.all())
        )
        self.assertEqual(
            list(response.context_data['books']),
            list(Book.objects.filter(title__icontains='new').order_by('year_of_publication'))
        )

    def test_user_library_view(self):
        create_book_in_db(title='Second New Book')
        UserBookInstance.objects.create(user=self.user, book=Book.objects.get(title='Second New Book'), is_read=True)

        url = reverse('library:user_books')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse('account:login')
        self.assertIn(login_url, response.url)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context_data['user_books'].values_list('id', flat=True)),
            set(UserBookInstance.objects.filter(user=self.user).values_list('id', flat=True))
        )
        response = self.client.get(reverse('library:user_books') + '?filter=read')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context_data['user_books'].values_list('id', flat=True)),
            set(UserBookInstance.objects.filter(user=self.user, is_read=True).values_list('id', flat=True))
        )
        response = self.client.get(reverse('library:user_books') + '?filter=unread')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context_data['user_books'].values_list('id', flat=True)),
            set(UserBookInstance.objects.filter(user=self.user, is_read=False).values_list('id', flat=True))
        )

    def test_user_library_filter_view(self):
        create_book_in_db(title='Second New Book')
        UserBookInstance.objects.create(user=self.user, book=Book.objects.get(title='Second New Book'), is_read=True)

        url = reverse('library:user_books_filter')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse('account:login')
        self.assertIn(login_url, response.url)

        self.client.force_login(self.user)

        response = self.client.get(reverse('library:user_books_filter') + '?filter=read')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context_data['user_books'].values_list('id', flat=True)),
            set(UserBookInstance.objects.filter(user=self.user, is_read=True).values_list('id', flat=True))
        )

    def test_add_book_view(self):
        url = reverse('library:add_book')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse('account:login')
        self.assertIn(login_url, response.url)

        self.client.force_login(self.user)
        response: TemplateResponse = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context_data['form'].is_valid())

        post_data = {
            'title': 'TestAddBookView',
            'description': 'description',
            'authors': 1,
            'genre': (1, 2),
            'year_of_publication': 2000,
            'file': get_mock_file('TestFile.pdf', 10),
        }
        self.assertFalse(Book.objects.filter(title='TestAddBookView').exists())
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title='TestAddBookView').exists())
        self.assertEqual(response.url, reverse('account:user_account'))
