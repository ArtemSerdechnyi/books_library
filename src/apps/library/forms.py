from django import forms

from utils.utils import get_minimal_book_year, get_maximal_book_year
from apps.library.models import Book


class BookForm(forms.ModelForm):
    """
    Form for creating book instance.
    """

    class Meta:
        model = Book
        fields = ['title', 'description', 'authors', 'genre', 'year_of_publication', 'file']

        help_texts = {
            'title': 'Enter the title of the book.',
            'description': 'Enter a description for the book (optional).',
            'authors': 'Select the author(s) of the book.',
            'genre': 'Select the genre(s) of the book.',
            'year_of_publication': 'Enter the year when the book was published.',
            'file': 'Upload the file of the book.',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'year_of_publication': forms.NumberInput(attrs={'min': get_minimal_book_year(),
                                                            'max': get_maximal_book_year()}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("File field cannot be empty")
        return cleaned_data
