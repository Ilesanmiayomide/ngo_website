import os
import requests

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST


def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def programs(request):
    return render(request, 'programs.html')


@require_POST
def create_donation(request):
    access_token = get_access_token()

    order_data = {
        'intent': 'CAPTURE',
        'purchase_units': [
            {
                'amount': {
                    'currency_code': 'USD',
                    'value': '10.00'
                }
            }
        ],
        'application_context': {
            'return_url': request.build_absolute_uri(reverse('paypal_success')),
            'cancel_url': request.build_absolute_uri(reverse('paypal_cancel'))
        }
    }

    response = requests.post(
        f'{settings.PAYPAL_BASE_URL}/v2/checkout/orders',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        },
        json=order_data
    )

    if response.status_code != 201:
        return HttpResponseBadRequest(
            f'PayPal order creation failed: {response.status_code} - {response.text}'
        )

    data = response.json()
    for link in data.get('links', []):
        if link.get('rel') == 'approve':
            return redirect(link['href'])

    return HttpResponseBadRequest('Could not find PayPal approval link.')


def paypal_success(request):
    token = request.GET.get('token')
    if not token:
        return HttpResponseBadRequest('Missing PayPal token.')

    access_token = get_access_token()
    response = requests.post(
        f'{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{token}/capture',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    )

    if response.status_code not in (200, 201):
        return HttpResponseBadRequest(
            f'PayPal payment capture failed: {response.status_code} - {response.text}'
        )

    data = response.json()
    return render(request, 'paypal_success.html', {'paypal_data': data})


def paypal_cancel(request):
    return render(request, 'paypal_cancel.html')


def get_access_token():
    response = requests.post(
        f'{settings.PAYPAL_BASE_URL}/v1/oauth2/token',
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
        headers={'Accept': 'application/json'},
        data={'grant_type': 'client_credentials'},
    )

    if response.status_code != 200:
        raise RuntimeError(
            f'PayPal auth failed: {response.status_code} - {response.text}'
        )

    return response.json().get('access_token')
