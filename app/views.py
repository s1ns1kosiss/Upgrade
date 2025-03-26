from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from .models import Product,Order,OrderDetail
import json
from django.http import JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
def home(req):
    products = Product.objects.all()
    return render(req, 'home/index.html', {'products': products})

def prodDetail(req,id):
    product = Product.objects.get(id=id)
    return render(req,'productDetail/index.html',{'product':product})
