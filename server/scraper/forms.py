from django import forms

class SearchForm(forms.Form):
    url = forms.URLField(
        label="URL",
        widget=forms.URLInput(attrs={
            "placeholder": "https://example.com",
            "style": "width: 100%; padding: 8px; border-radius: 8px; border: 1px solid #ccc;"
        }),
    )
