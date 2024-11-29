from django.shortcuts import render
from django.contrib.auth.decorators import login_required  
from .forms import *
from .models import *

# Create your views here.

def Home(request):
    buscar = book.objects.all().order_by('book_id')[:3]
    data = {
        'forms': buscar
    }
    return render(request, 'index.html', data)

def Visualize(request):
    buscar = book.objects.all()
    data = {
        'forms': buscar
    }
    return render(request, 'pages/visualize.html', data)

@login_required  
def Add(request):
    data = {
        'forms': Newbook()
    }
    if request.method == 'POST':
        query = Newbook(data=request.POST, files=request.FILES)
        if query.is_valid():
            query.save()
            data['message'] = "Datos registrados"
        else:
            data['forms'] = Newbook()
    return render(request, 'pages/add.html', data)