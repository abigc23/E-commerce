from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(author)
admin.site.register(book)
admin.site.register(genre)