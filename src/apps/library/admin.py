from django.contrib import admin

from .models import Country, Author, Genre, Book, UserBookInstance


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    show_full_result_count = False

    list_display = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    show_full_result_count = False

    list_display = ['full_name', 'country']
    search_fields = ['full_name']
    list_filter = ['country']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    show_full_result_count = False

    list_display = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    show_full_result_count = False

    list_display = ['title', 'year_of_publication']
    filter_horizontal = ['authors', 'genre']
    search_fields = ['title']




@admin.register(UserBookInstance)
class UserBookInstanceAdmin(admin.ModelAdmin):
    show_full_result_count = False

    list_display = ['user', 'book', 'is_read']
    list_filter = ['user', 'is_read']
