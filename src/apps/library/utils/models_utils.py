from django.core.exceptions import ValidationError


def get_accepted_image_extensions():
    return 'png', 'jpg', 'jpeg'


def validate_image_size(value):
    limit = 5 * 1024 * 1024
    filesize = value.size
    if filesize > limit:
        raise ValidationError('The maximum file size that can be uploaded is 5MB')


def get_accepted_book_extensions():
    return 'pdf', 'doc', 'docx', 'txt'


def validate_book_size(value):
    limit = 50 * 1024 * 1024
    filesize = value.size
    if filesize > limit:
        raise ValidationError('The maximum file size that can be uploaded is 25MB')
