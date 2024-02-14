from django.urls import path, re_path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.home_page_view, name='index'),
]