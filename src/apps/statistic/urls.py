from django.urls import path, re_path

from . import views

app_name = 'statistic'

urlpatterns = [
    path('', views.home_page_view, name='index'),
    path('genres_statistic/', views.genres_statistic_view, name='genres_statistic'),
    path('fig_genres_statistic/', views.fig_genres_statistic_view, name='fig_genres_statistic'),
    path('authors_statistic/', views.authors_statistic_view, name='authors_statistic'),
    path('books_read_statistic/', views.books_read_statistics_view, name='books_read_statistic'),
    path('general_statistics/', views.general_statistics_view, name='general_statistics'),

]
