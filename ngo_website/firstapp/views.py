import os
from decimal import Decimal, InvalidOperation
import requests
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def programs(request):
    return render(request, 'programs.html')


def donate(request):
    return render(request, 'donate.html', {
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'venmo_url': settings.VENMO_DONATION_URL
    })


@csrf_exempt
@require_POST
def create_paypal_order(request):
    try:
        data = json.loads(request.body)
        amount_raw = data.get('amount', '10.00')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    try:
        amount = Decimal(str(amount_raw))
    except InvalidOperation:
        return JsonResponse({'error': 'Invalid donation amount'}, status=400)

    if amount <= 0:
        return JsonResponse({'error': 'Donation amount must be greater than 0'}, status=400)

    amount = amount.quantize(Decimal('0.01'))

    access_token = get_access_token()
    order_data = {
        'intent': 'CAPTURE',
        'purchase_units': [
            {
                'amount': {
                    'currency_code': 'USD',
                    'value': str(amount)
                }
            }
        ]
    }

    response = requests.post(
        f'{settings.PAYPAL_BASE_URL}/v2/checkout/orders',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        },
        json=order_data
    )

    if response.status_code not in (200, 201):
        return JsonResponse({
            'error': f'Payment order creation failed: {response.status_code}'
        }, status=400)

    order_data = response.json()
    return JsonResponse({
        'id': order_data['id']
    })


@require_POST
def create_donation(request):
    access_token = get_access_token()
    amount_raw = request.POST.get('amount', '10.00').strip()

    try:
        amount = Decimal(amount_raw)
    except InvalidOperation:
        return HttpResponseBadRequest('Invalid donation amount.')

    if amount <= 0:
        return HttpResponseBadRequest('Donation amount must be greater than 0.')

    amount = amount.quantize(Decimal('0.01'))

    order_data = {
        'intent': 'CAPTURE',
        'purchase_units': [
            {
                'amount': {
                    'currency_code': 'USD',
                    'value': str(amount)
                }
            }
        ],
        'application_context': {
            'return_url': request.build_absolute_uri(reverse('paypal_success')),
            'cancel_url': request.build_absolute_uri(reverse('paypal_cancel'))
        },
        'payment_source': {'paypal': {}}
    }

    response = requests.post(
        f'{settings.PAYPAL_BASE_URL}/v2/checkout/orders',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        },
        json=order_data
    )

    if response.status_code not in (200, 201):
        return HttpResponseBadRequest(
            f'Payment order creation failed: {response.status_code} - {response.text}'
        )

    data = response.json()
    for link in data.get('links', []):
        if link.get('rel') in ['approve', 'payer-action']:
            return redirect(link['href'])

    return HttpResponseBadRequest('Could not find payment approval link.')


def paypal_success(request):
    order_id = request.GET.get('token')  # For server-side flow
    if not order_id:
        order_id = request.GET.get('order_id')  # For JS SDK flow

    if not order_id:
        return HttpResponseBadRequest('Missing PayPal order ID.')

    # For JS SDK flow, the capture is already done on the frontend
    # For server-side flow, we need to capture here
    if request.GET.get('token'):  # Server-side flow
        access_token = get_access_token()
        response = requests.post(
            f'{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture',
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
        return render(request, 'paypal_success.html', {'paypal_data': data, 'order_id': order_id})
    else:
        # JS SDK flow - order is already captured
        return render(request, 'paypal_success.html', {'order_id': order_id})


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
