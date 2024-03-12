from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile


def validate_file_size(size_in_mb, file: FieldFile):
    """
    Validates the size of a file.
    """
    limit = size_in_mb * 1024 * 1024
    filesize = file.size
    if filesize > limit:
        raise ValidationError(f'The maximum file size that can be uploaded is {size_in_mb}MB')


def get_accepted_image_extensions():
    """
    Returns the accepted image file extensions.
    """
    return 'png', 'jpg', 'jpeg'


def validate_image_size(file):
    """
    Validates the size of an image file.
    """
    max_size = 5
    validate_file_size(max_size, file)


def get_accepted_book_extensions():
    """
    Returns the accepted book file extensions.
    """
    return 'pdf', 'doc', 'docx', 'txt'


def validate_book_size(file):
    """
    Validates the size of a book file.
    """
    max_size = 30
    validate_file_size(max_size, file)


class FullCleanBeforeSaveMixin:
    """
    A mixin that ensures full cleaning before saving a model instance.
    """

    def save(self, *args, **kwargs):
        """
        Overrides the save method to perform full cleaning before saving the model instance.
        """
        self.full_clean()
        super().save(*args, **kwargs)
