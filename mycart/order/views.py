from django.shortcuts import render,redirect
from django.http import HttpResponse
from cart.models import *
from .forms import Orderform
from .models import *
import datetime
from django.contrib.auth.decorators import login_required

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='customer_login_view')
def place_order(request):
    current_user = request.user
    cart_items = Cart_item.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('shop')

    grand_total = 0
    tax = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phonenumber')
        address_line1 = request.POST.get('addressline1')
        address_line2 = request.POST.get('addressline2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        order_note = request.POST.get('ordernote')
        order_total = grand_total
        ip = request.META.get('REMOTE_ADDR')

        # Generate order number
        yr = int(datetime.datetime.today().strftime('%Y'))
        dt = int(datetime.datetime.today().strftime('%d'))
        mt = int(datetime.datetime.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime('%Y%m%d')

        # Create the order
        order = Order.objects.create(
            user=current_user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone_number,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            order_note=order_note,
            tax=tax,
            order_total=order_total,
            ip=ip,
            country=country,
            state=state
        )
        
        # Update order number after the order is created
        order_number = current_date + str(order.id)
        order.order_number = order_number
        order.save()  # Save the updated order with the order number

        return render(request, 'cart/checkout.html', {
            'cart_items': cart_items,
            'grand_total': grand_total,
            'order': order,
            'total': total,
            'tax':tax
        })
    
    return render(request, 'cart/place_order.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
        'total': total
    })

    
def checkout(request):
    return render(request,'cart/checkout.html',)


def create_order_with_paypal(amount):
    client_id = 'ARQ65oYr2XSWyrI14W-miP4nXCjA496XZyBRPzxUY8W1GJhiaGH5kWeJwIwnVNbe1qij70XxZsdMBxmm'
    secret = 'EM_4v8bAdMXaEmKWeSojqIt5eEpEOEXuaq7aZCCLL6QwdoVvtTsuoS8e0yHnt5lMFcU6dXJx3kpQBBSH'
    api_url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders'

    response = requests.post(
        'https://api-m.sandbox.paypal.com/v1/oauth2/token',
        auth=(client_id, secret),
        data={'grant_type': 'client_credentials'}
    )

    if response.status_code != 200:
        return {'error': 'Failed to get access token', 'details': response.json()}

    access_token = response.json().get('access_token')

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": amount
            }
        }]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    order_response = requests.post(api_url, json=order_data, headers=headers)

    if order_response.status_code != 201:
        return {'error': 'Failed to create order', 'details': order_response.json()}

    return order_response.json()


@csrf_exempt
def create_paypal_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        print(data)

        order_response = create_order_with_paypal(amount)

        if 'error' in order_response:
            return JsonResponse(order_response, status=400)  # Return error details with a 400 status

        return JsonResponse({'id': order_response.get('id')})  # Return the order ID
    return JsonResponse({'id': order_response.get('id')})  # Return the order ID



@csrf_exempt  # For testing; handle CSRF appropriately in production
def capture_paypal_order(request, order_id):
    if request.method == 'POST':
        # Set your PayPal API credentials
        client_id = 'ARQ65oYr2XSWyrI14W-miP4nXCjA496XZyBRPzxUY8W1GJhiaGH5kWeJwIwnVNbe1qij70XxZsdMBxmm'
        secret = 'EM_4v8bAdMXaEmKWeSojqIt5eEpEOEXuaq7aZCCLL6QwdoVvtTsuoS8e0yHnt5lMFcU6dXJx3kpQBBSH'
        api_url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture'

        # Get an access token
        response = requests.post(
            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
            auth=(client_id, secret),
            data={'grant_type': 'client_credentials'}
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to get access token', 'details': response.json()}, status=400)

        access_token = response.json().get('access_token')

        # Capture the order
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        capture_response = requests.post(api_url, headers=headers)

        if capture_response.status_code != 201:  # 201 Created
            return JsonResponse({'error': 'Failed to capture order', 'details': capture_response.json()}, status=400)

        return JsonResponse(capture_response.json())
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def receive_transaction_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract relevant information from the transaction data
        payment_id = data['purchase_units'][0]['payments']['captures'][0]['id']
        payment_method = 'PayPal'  # Or extract from data if available
        amount_paid = data['purchase_units'][0]['payments']['captures'][0]['amount']['value']
        status = data['purchase_units'][0]['payments']['captures'][0]['status']
        
        # Create a Payment instance
        payment = Payment(
            user=request.user,  # Ensure the user is authenticated
            payment_id=payment_id,
            payment_method=payment_method,
            amount_paid=amount_paid,
            status=status
        )
        payment.save()  # Save the payment record

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)
