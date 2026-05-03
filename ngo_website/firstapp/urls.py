from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('programs/', views.programs, name='programs'),
    path('paypal/donate/', views.create_donation, name='create_donation'),
    path('paypal/success/', views.paypal_success, name='paypal_success'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
]
