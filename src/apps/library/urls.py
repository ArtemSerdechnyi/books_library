from django.urls import path, re_path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.home_page_view, name='index'),
    path(f'{app_name}/book/<slug:slug>/', views.BookView.as_view(), name='book'),
    path(f'{app_name}/', views.LibraryView.as_view(), name='library'),
    path(f'{app_name}/add_book/', views.AddBookView.as_view(), name='add_book'),
    path(f'{app_name}/library_search/', views.LibrarySearchView.as_view(), name='library_search'),
    path('user_books/', views.UserLibraryView.as_view(), name='user_books'),
    path('add_book_to_user_library/<int:id>/', views.add_book_to_user_library_view, name='add_book_to_user_library'),
    path('remove_book_from_user_library/<int:id>/', views.remove_book_from_user_library_view,
         name='remove_book_from_user_library'),
    path('change_book_read_status/<int:id>/', views.change_book_read_status_view, name='change_book_read_status'),
    path('user_books_filter/', views.UserLibraryFilterView.as_view(), name='user_books_filter'),
]
