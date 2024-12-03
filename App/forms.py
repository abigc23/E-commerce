from django import forms
from .models import *

class Newbook(forms.ModelForm):
    class Meta:
        model=book
        fields='__all__'

class NewAuthor(forms.ModelForm):
    class Meta:
        model = author
        fields = '__all__'

class NewGenre(forms.ModelForm):
    class Meta:
        model = genre
        fields = '__all__'        