from django.shortcuts import render
from django.contrib.auth.decorators import login_required  
from .forms import *
from .models import *

# Create your views here.

def Home(request):
    buscar = Book.objects.all().order_by('book_id')[:3]
    data = {
        'forms': buscar
    }
    return render(request, 'index.html', data)

def Visualize(request):
    buscar = Book.objects.all()
    data = {
        'forms': buscar
    }
    return render(request, 'pages/visualize.html', data)

@login_required  
def Add(request):
    data = {
        'forms': NewBook()
    }
    if request.method == 'POST':
        query = NewBook(data=request.POST, files=request.FILES)
        if query.is_valid():
            query.save()
            data['message'] = "Datos registrados"
        else:
            data['forms'] = NewBook()
    return render(request, 'pages/add.html', data)