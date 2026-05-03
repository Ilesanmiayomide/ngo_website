from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect

PAYPAL_CLIENT_ID = "your_sandbox_client_id"
PAYPAL_SECRET = "your_sandbox_secret"
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"
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



PAYPAL_CLIENT_ID = "AWqyMA_Z0XW4OjpnyotbkOd1CBZAXpE9zEFPAfG0btqabAelBtfHjQlOcwhN6OPOgDhtDFagW70-sVz8"
PAYPAL_SECRET = "EE8V02eG6_-ZkNIhxF8r-WB2MKGYrfzyD2jvvWoE5x_AFQJQGk8YrhVkjWkHmW2abjTyPVgyErEEPTVp"
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"


def get_access_token():
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
    )
    return response.json()["access_token"]


def create_donation(request):
    access_token = get_access_token()

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": "10.00"
                }
            }
        ],
        "application_context": {
            "return_url": "http://localhost:8000/paypal/success/",
            "cancel_url": "http://localhost:8000/paypal/cancel/"
        }
    }

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json=order_data
    )

    data = response.json()

    # extract approval link
    for link in data["links"]:
        if link["rel"] == "approve":
            return redirect(link["href"])
        
def paypal_success(request):
    token = request.GET.get("token")
    access_token = get_access_token()

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders/{token}/capture",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )

    return HttpResponse("Payment successful")