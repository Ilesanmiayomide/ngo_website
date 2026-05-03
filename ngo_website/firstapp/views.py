from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from django.shortcuts import render

def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def programs(request):
    return render(request, 'programs.html')


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def programs(request):
    return render(request, 'programs.html')