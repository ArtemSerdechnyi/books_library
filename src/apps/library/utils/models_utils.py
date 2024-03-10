from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile


def validate_file_size(size_in_mb, file: FieldFile):
    limit = size_in_mb * 1024 * 1024
    filesize = file.size
    if filesize > limit:
        raise ValidationError(f'The maximum file size that can be uploaded is {size_in_mb}MB')


def get_accepted_image_extensions():
    return 'png', 'jpg', 'jpeg'


def validate_image_size(file):
    max_size = 5
    validate_file_size(max_size, file)


def get_accepted_book_extensions():
    return 'pdf', 'doc', 'docx', 'txt'


def validate_book_size(file):
    max_size = 30
    validate_file_size(max_size, file)


class FullCleanBeforeSaveMixin:
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
