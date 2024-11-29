from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required  
from .forms import *
from .models import *
import mercadopago
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q

# Create your views here.
def Home(request):
    genres = genre.objects.all() 
    buscar = book.objects.all().order_by('-publication_date')[:6]  

    data = {
        'books': buscar  
    }
    return render(request, 'index.html', data)

def login_views(request):
    if request.method == 'GET':
        return render(request, 'login/login.html', {
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                "error": 'username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect(to='home')

def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.save()
                login(request, user) 
                return redirect('home')
            except IntegrityError:
                return render(request, 'login/signup.html', {
                    "error": 'El nombre de usuario ya está en uso.'
                })
        else:
            return render(request, 'login/signup.html', {
                "error": 'Las contraseñas no coinciden.'
            })
    else:
        return render(request, 'login/signup.html')


def salir(request):
    logout(request)
    return redirect(to='home')

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

def carrito(request):
    # Obtener los productos del carrito del cliente
    customer_id = request.user.id  
    carrito_items = cartitem.objects.filter(customer_id=customer_id)
    
    if not carrito_items:
        return render(request, 'carrito/empty_cart.html', {"message": "Tu carrito está vacío."})

    total_amount = sum([item.quantity * item.book.price for item in carrito_items])
    
    data = {
        'carrito_items': carrito_items,
        'total_amount': total_amount,
    }

    return render(request, 'carrito/carrito.html', data)

def books_by_genre(request, genre_id):
    selected_genre = genre.objects.filter(genre_id=genre_id).first()

    if not selected_genre:
        selected_genre = None

    books_in_genre = book.objects.filter(genre=selected_genre) if selected_genre else []

    return render(request, 'books_by_genre.html', {
        'genre': selected_genre,
        'books': books_in_genre,
    })



@login_required
def pago(request):
    customer_id = request.user.id
    carrito = cartitem.objects.filter(customer_id=customer_id)
    
    if not carrito:
        return render(request, 'carrito/empty_cart.html', {"message": "Tu carrito está vacío."})

    total_amount = sum([item.quantity * item.book.price for item in carrito])
    
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    items = []
    for item in carrito:
        items.append({
            "title": item.book.title,
            "quantity": item.quantity,
            "unit_price": float(item.book.price),
        })

    preference_data = {
        "items": items,
        "back_urls": {
            "success": request.build_absolute_uri('/payment/success/'),
            "failure": request.build_absolute_uri('/payment/failure/'),
            "pending": request.build_absolute_uri('/payment/pending/'),
        },
        "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    preference_id = preference_response["response"]["id"]

    order_obj = order.objects.create(
        customer_id=customer_id,
        order_date=request.timestamp,
        status="Pendiente",
        total_amount=total_amount,
        total_paid=0,
    )

    order_obj.payment_url = f"https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id={preference_id}"
    order_obj.save()

    data = {
        'carrito_items': carrito,
        'total_amount': total_amount,
        'payment_url': order_obj.payment_url,
    }

    return render(request, 'carrito/pago.html', data)


def PagoSuccess(request):
    return render(request, 'carrito/pago_success.html', {"message": "¡Pago exitoso!"})

def PagoFailure(request):
    return render(request, 'carrito/pago_failure.html', {"message": "El pago ha fallado. Inténtalo de nuevo."})

def PagoPending(request):
    return render(request, 'carrito/pago_pending.html', {"message": "El pago está pendiente."})
