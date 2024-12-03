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
from django.utils.timezone import now



# Create your views here.
def Home(request):
    genres = genre.objects.all() 
    buscar = book.objects.all().order_by('-publication_date')[:6]  

    data = {
        'books': buscar  
    }
    return render(request, 'index.html', data)


def get_or_create_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# Vista para login
def login_views(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login/login.html', {
                "error": 'El nombre de usuario o la contraseña son incorrectos.'
            })
        else:
            login(request, user)
            if hasattr(user, 'customer'):
                return redirect('userprofile')
            return redirect('home')
    return render(request, 'login/login.html')


# Vista para signup
def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Crear el usuario
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()

                # Crear el cliente
                customer_obj = customer.objects.create(
                    user=user,
                    phone=request.POST['phone'],
                    address=request.POST['address'],
                    city=request.POST['city'],
                    postal_code=request.POST['postal_code'],
                    country=request.POST['country'],
                )
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
    return render(request, 'login/signup.html')

# Vista para logout
def salir(request):
    if request.user.is_authenticated:
        logout(request)  
    return redirect('home')  

def Visualize(request):
    buscar = book.objects.all()
    data = {
        'forms': buscar
    }
    return render(request, 'pages/visualize.html', data)


def userprofile(request):
    if request.user.is_authenticated:
        try:
            customer_obj = request.user.customer
            data = {
                'user': {
                    'name': customer_obj.user.username,
                    'phone': customer_obj.phone,
                    'address': customer_obj.address,
                    'city': customer_obj.city,
                    'postal_code': customer_obj.postal_code,
                    'country': customer_obj.country,
                },
                'is_authenticated': True,
            }
        except customer.DoesNotExist:
            data = {
                'is_authenticated': True,
                'error': 'No hay información adicional disponible.',
            }
    else:
        data = {
            'is_authenticated': False,
        }
    return render(request, 'userprofile.html', data)

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
    if request.user.is_authenticated:
        customer_id = request.user.customer.customer_id
        carrito_items = cartitem.objects.filter(customer_id=customer_id).select_related('book')
    else:
        session_key = get_or_create_session_key(request)
        carrito_items = cartitem.objects.filter(session_key=session_key).select_related('book')

    if not carrito_items:
        return render(request, 'carrito/carrito.html', {"message": "Tu carrito está vacío."})

    total_amount = sum(item.quantity * item.book.price for item in carrito_items)

    # Configuración de Mercado Pago
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    items = []
    for item in carrito_items:
        items.append({
            "title": item.book.title,
            "quantity": item.quantity,
            "unit_price": float(item.book.price),
        })

    # Datos de la preferencia
    preference_data = {
        "items": items,
        "back_urls": {
            "success": request.build_absolute_uri('/payment/success/'),
            "failure": request.build_absolute_uri('/payment/failure/'),
            "pending": request.build_absolute_uri('/payment/pending/'),
        },
        "auto_return": "approved",
    }

    # Crear la preferencia y la orden
    preference_response = sdk.preference().create(preference_data)
    preference_id = preference_response["response"]["id"]

    order_obj = order.objects.create(
        customer_id=customer_id if request.user.is_authenticated else None,
        order_date=now(),
        status="Pendiente",
        total_amount=total_amount,
        total_paid=0,
    )

    order_obj.payment_url = f"https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id={preference_id}"
    order_obj.save()

    data = {
        'carrito_items': carrito_items,
        'total_amount': total_amount,
        'payment_url': order_obj.payment_url,
    }

    return render(request, 'carrito/carrito.html', data)

    
def remove_from_cart(request, book_id):
    if request.user.is_authenticated:
        customer_obj = request.user.customer
        cart_item = cartitem.objects.filter(customer=customer_obj, book_id=book_id).first()
        if cart_item:
            cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        if str(book_id) in cart:
            del cart[str(book_id)]
            request.session['cart'] = cart  

    return redirect('carrito')



def books_by_genre(request, genre_id):
    selected_genre = genre.objects.filter(genre_id=genre_id).first()

    if not selected_genre:
        selected_genre = None

    books_in_genre = book.objects.filter(genre=selected_genre) if selected_genre else []

    return render(request, 'books_by_genre.html', {
        'genre': selected_genre,
        'books': books_in_genre,
    })

def add_to_cart(request, book_id):
    session_key = get_or_create_session_key(request)
    print(f"Session Key: {session_key}")
    
    selected_book = get_object_or_404(book, book_id=book_id)
    print(f"Selected Book: {selected_book.title}, ID: {selected_book.book_id}")
    
    if request.user.is_authenticated:
        print("User is authenticated.")
        customer_obj = request.user.customer
        print(f"Customer Object: {customer_obj}")
        
        cart_item, created = cartitem.objects.get_or_create(
            customer=customer_obj,
            book=selected_book,
            defaults={'quantity': 1}
        )
    else:
        print("User is not authenticated.")
        cart_item, created = cartitem.objects.get_or_create(
            session_key=session_key,
            book=selected_book,
            defaults={'quantity': 1}
        )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        print(f"Quantity updated: {cart_item.quantity}")
    
    return redirect('carrito')

def PagoSuccess(request):
    return render(request, 'carrito/pago_success.html', {"message": "¡Pago exitoso!"})

def PagoFailure(request):
    return render(request, 'carrito/pago_failure.html', {"message": "El pago ha fallado. Inténtalo de nuevo."})

def PagoPending(request):
    return render(request, 'carrito/pago_pending.html', {"message": "El pago está pendiente."})
