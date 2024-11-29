from django.urls import path
#-->Importamos las Vistas para las URL
from .views import *
from .forms import *

urlpatterns = [
    #-->URL, FUNCION, NOMBRE PARA HTML
    path('', Home, name='home'),
    path('visualize/', Visualize, name='visualize'),
    path('add/', Add, name="add"),
    path('carrito/', carrito, name='carrito'),  # Página del carrito
    path('pago/', pago, name='pago'),  # Página para hacer el pago
    path('categoria/<int:genre_id>/', books_by_genre, name='books_by_genre'),
    path('payment/success/', PagoSuccess, name='pago_success'),
    path('payment/failure/', PagoFailure, name='pago_failure'),
    path('payment/pending/', PagoPending, name='pago_pending'),
]
