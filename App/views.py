from django.shortcuts import render
from .forms import *
from .models import *


# Create your views here.

def Home(request):
    buscar=Book.objects.all().order_by('book_id')[:3]
    data={
        'forms':buscar
    }
    return render (request,'index.html',data)

