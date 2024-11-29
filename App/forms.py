from django import forms
from .models import *

class Newbook(forms.ModelForm):
    class Meta:
        model=book
        fields='__all__'