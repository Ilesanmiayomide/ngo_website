from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from django.shortcuts import render

def home(request):
    return render(request, 'base.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')