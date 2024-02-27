from django.urls import path, re_path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.home_page_view, name='index'),
    path(f'{app_name}/book/<slug:slug>/', views.BookView.as_view(), name='book'),
    path(f'{app_name}/', views.Library.as_view(), name='library'),
    path('add_book/', views.AddBook.as_view(), name='add_book'),
    path('library_search/', views.LibrarySearch.as_view(), name='library_search'),
]