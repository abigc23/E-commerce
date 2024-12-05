from django import forms
from .models import *

class Newbook(forms.ModelForm):
    class Meta:
        model = book
        fields = ['title', 'author', 'publication_date', 'isbn', 'price', 'cover_image', 'stock','language','page_count','genre']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
        }

class NewAuthor(forms.ModelForm):
    class Meta:
        model = author
        fields = ['name', 'author_image', 'bio', 'birth_date', 'nationality']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class NewGenre(forms.ModelForm):
    class Meta:
        model = genre
        fields = '__all__'        