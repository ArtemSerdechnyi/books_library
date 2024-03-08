from django import forms

from utils.utils import get_minimal_book_year, get_maximal_book_year


class YearFilterForm(forms.Form):
    start_year = forms.IntegerField(
        label='Start Year',
        required=False,
        min_value=get_minimal_book_year(),
        max_value=get_maximal_book_year(),
    )
    end_year = forms.IntegerField(
        label='End Year',
        required=False,
        min_value=get_minimal_book_year(),
        max_value=get_maximal_book_year(),
    )

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        end_year = cleaned_data.get("end_year")

        if start_year is None:
            cleaned_data['start_year'] = get_minimal_book_year()
        if end_year is None:
            cleaned_data['end_year'] = get_maximal_book_year()

        if start_year is not None and end_year is not None and start_year > end_year:
            raise forms.ValidationError("Start year should not be greater than end year.")
        return cleaned_data
