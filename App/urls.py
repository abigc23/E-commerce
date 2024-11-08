from django.urls import path
#-->Importamos las Vistas para las URL
from .views import *
from .forms import *

urlpatterns = [
    #-->URL, FUNCION, NOMBRE PARA HTML
    path('', Home, name='home'),
    path('visualize', Visualize, name='visuaize'),
    path('add', Add, name="add"),
]
