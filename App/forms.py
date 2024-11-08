from django import forms
from .models import *

class NewBook(forms.ModelForm):
    class Meta:
        model=Book
        fields='__all__'