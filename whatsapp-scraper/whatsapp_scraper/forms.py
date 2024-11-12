from django import forms
from datetime import date


class DateFilterForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        label="Filter by date",
    )
