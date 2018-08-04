from django import forms
from .models import Album


class AlbumAddForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Navn på album",
            }
        ))
    description = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "form-control",
            "placeholder": "Albumbeskrivelse",
            }
        ))

    class Meta:
        model = Album
        fields = ["name", "description"]
