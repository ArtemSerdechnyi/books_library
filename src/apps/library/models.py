from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify


# from .utils import get_book_path, get_book_image_path


class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Author(models.Model):
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


class Genre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='book_images', default='default_book_image.jpg')
    description = models.TextField(null=True, blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    genre = models.ManyToManyField(Genre, related_name='books')
    year_of_publication = models.IntegerField(
        validators=[MinValueValidator(-1000), MaxValueValidator(timezone.now().year)],
    )
    file = models.FileField(upload_to='book_files')
    added_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='added_books')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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
