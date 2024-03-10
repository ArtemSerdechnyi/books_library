from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from utils.utils import get_minimal_book_year, get_maximal_book_year
from .utils.models_utils import (
    get_accepted_book_extensions,
    validate_book_size,
    get_accepted_image_extensions,
    validate_image_size,
    FullCleanBeforeSaveMixin
)


class Country(FullCleanBeforeSaveMixin, models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Author(FullCleanBeforeSaveMixin, models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, editable=False, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=255, editable=False)

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f'{self.first_name} {self.last_name}'
        if not self.slug:
            self.slug = slugify(self.full_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Genre(FullCleanBeforeSaveMixin, models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(FullCleanBeforeSaveMixin, models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='book_images', default='default_book_image.jpg',
                              validators=[FileExtensionValidator(get_accepted_image_extensions()), validate_image_size])
    description = models.TextField(null=True, blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    genre = models.ManyToManyField(Genre, related_name='books')
    year_of_publication = models.IntegerField(
        validators=[MinValueValidator(get_minimal_book_year()), MaxValueValidator(get_maximal_book_year())],
    )
    file = models.FileField(upload_to='book_files',
                            validators=[FileExtensionValidator(get_accepted_book_extensions()), validate_book_size])
    added_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='added_books')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class UserBookInstance(FullCleanBeforeSaveMixin, models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='instances')
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.book.title

    class Meta:
        unique_together = ('user', 'book')
