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
from django.db.models import ObjectDoesNotExist




# Create your views here.
# ruben
def Home(request):
    genres = genre.objects.all() 
    buscar = book.objects.all()
    # order_by('-publication_date')[:6]  

    data = {
        'books': buscar  
    }
    return render(request, 'index.html', data)

def get_or_create_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# Vista para login
def login_views(request, template_name='login/login.html'):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, template_name, {
                "error": 'El nombre de usuario o la contraseña son incorrectos.'
            })
        else:
            login(request, user)
            if hasattr(user, 'customer'):
                return redirect('userprofile')
            return redirect('home')
    return render(request, template_name)



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
        'books': buscar
    }
    return render(request, 'pages/visualize.html', data)

def book_detail(request, book_id):
    libro = get_object_or_404(book, book_id=book_id)
    return render(request, 'pages/book_detail.html', {'book': libro})

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
def Add_book_author_genre(request):
    data = {
        'book_form': Newbook(),
        'author_form': NewAuthor(),
        'genre_form': NewGenre(),
    }

    if request.method == 'POST':
        book_query = Newbook(data=request.POST, files=request.FILES)
        if 'book_title' in request.POST:  
            if book_query.is_valid():
                book_query.save()
                data['message_book'] = "Libro registrado correctamente"
            else:
                data['message_book'] = "Error al registrar el libro"

        # Formulario de autor
        author_query = NewAuthor(data=request.POST)
        if 'author_name' in request.POST:
            if author_query.is_valid():
                author_query.save()
                data['message_author'] = "Autor registrado correctamente"
            else:
                data['message_author'] = "Error al registrar el autor"

        # Formulario de género
        genre_query = NewGenre(data=request.POST)
        if 'genre_name' in request.POST:  
            if genre_query.is_valid():
                genre_query.save()
                data['message_genre'] = "Género registrado correctamente"
            else:
                data['message_genre'] = "Error al registrar el género"

        data['book_form'] = book_query
        data['author_form'] = author_query
        data['genre_form'] = genre_query

    return render(request, 'pages/add.html', data)

# ruben
@login_required
def modificar_book_author_genre(request, book_id):
    try:
        libro = get_object_or_404(book, book_id=book_id)
        autor = libro.author
        genero = libro.genre
        
        book_form = Newbook(instance=libro)
        author_form = NewAuthor(instance=autor)
        genre_form = NewGenre(instance=genero) if genero else None

        if request.method == 'POST':
            if 'book_title' in request.POST:  
                book_form = Newbook(request.POST, request.FILES, instance=libro)
                if book_form.is_valid():
                    book_form.save()
                    return redirect('success_page')  

            if 'author_name' in request.POST:  
                author_form = NewAuthor(request.POST, instance=autor)
                if author_form.is_valid():
                    author_form.save()
                    return redirect('success_page')  

            if genero and 'genre_name' in request.POST:  
                genre_form = NewGenre(request.POST, instance=genero)
                if genre_form.is_valid():
                    genre_form.save()
                    return redirect('success_page')  

        data = {
            'book_form': book_form,
            'author_form': author_form,
            'genre_form': genre_form,
        }
        return render(request, 'pages/modificar.html', data)

    except Exception as e:
        print(f"Error: {e}")
        return redirect('error_page')


def carrito(request):
    carrito_items = []
    customer_id = None

    if request.user.is_authenticated:
        try:
            customer_id = request.user.customer.customer_id
            carrito_items = cartitem.objects.filter(customer_id=customer_id).select_related('book')
        except ObjectDoesNotExist:
            # Manejo del caso donde el usuario no tiene un perfil customer asociado
            return render(request, 'carrito/carrito.html', {
                "message": "No tienes un perfil de cliente asociado. Por favor, contacta al soporte."
            })
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

def error_page(request):
    return render(request, 'error_page.html', {
        'message': "Ha ocurrido un error. Por favor, contacta al soporte o inténtalo más tarde."
    })

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

@login_required
def add_to_cart(request, book_id):
    session_key = get_or_create_session_key(request)
    print(f"Session Key: {session_key}")
    
    selected_book = get_object_or_404(book, book_id=book_id)
    print(f"Selected Book: {selected_book.title}, ID: {selected_book.book_id}")
    
    if request.user.is_authenticated:
        print("User is authenticated.")
        try:
            customer_obj = request.user.customer
            print(f"Customer Object: {customer_obj}")
            
            cart_item, created = cartitem.objects.get_or_create(
                customer=customer_obj,
                book=selected_book,
                defaults={'quantity': 1}
            )
        except ObjectDoesNotExist:
            print("Authenticated user has no customer profile.")
            return redirect('error_page')  # Ajusta 'error_page' a la URL de tu página de error.
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
