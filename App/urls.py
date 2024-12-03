from django.urls import path
#-->Importamos las Vistas para las URL
from .views import *
from .forms import *

urlpatterns = [
    #-->URL, FUNCION, NOMBRE PARA HTML
    path('', Home, name='home'),
    path('visualize/', Visualize, name='visualize'),
    path('book/<int:book_id>/', book_detail, name='book_detail'),
    path('add/', Add_book_author_genre, name="add"),
    path('error_page/', error_page, name="error_page"),
    path('userprofile/', userprofile, name='userprofile'),
    path('carrito/', carrito, name='carrito'),
    path('modificar/<int:book_id>/', modificar_book_author_genre, name='modificar_book'),
    path('add_to_cart/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('carrito/remove/<int:book_id>/',remove_from_cart, name='remove_from_cart'),    
    path('categoria/<int:genre_id>/', books_by_genre, name='books_by_genre'),
    path('login/', login_views, name='signin'),
    path('signup/', signup, name='signup'),
    path('logout/', salir, name='salir'),
    path('payment/success/', PagoSuccess, name='pago_success'),
    path('payment/failure/', PagoFailure, name='pago_failure'),
    path('payment/pending/', PagoPending, name='pago_pending'),
]
