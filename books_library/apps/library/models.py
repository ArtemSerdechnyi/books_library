from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.datetime_safe import datetime

from .utils import get_book_path


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=255, editable=False)

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, ralated_name='books')
    genre = models.ManyToManyField(Genre, related_name='books')
    year_of_publication = models.IntegerField(
        validators=[MinValueValidator(-1000), MaxValueValidator(datetime.now().year)],
    )
    file = models.FileField(upload_to=get_book_path)

    class Meta:
        unique_together = ('title', 'authors')

    def __str__(self):
        return self.title


class UserBookInstance(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='instances')
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.book

    class Meta:
        unique_together = ('user', 'book')
