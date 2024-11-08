from django.shortcuts import render,get_object_or_404,redirect
from .forms import *
from .models import *
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q

# Create your views here.

