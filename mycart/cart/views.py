from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import Cart, Cart_item
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account.models import *


def _cart_id(request):
    cart=request.session.session_key
    print(cart)
    if not cart:
        cart=request.session.create()
    return cart



def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_id = _cart_id(request) 

    if request.user.is_authenticated:
        current_user = CustomerProfile.objects.filter(user__id=request.user.id)
        cart_str = str(cart_id).replace("\'", "\"")
        current_user.update(old_cart=str(cart_str))
        user = request.user  
    else:
        user = None  

    cart, created = Cart.objects.get_or_create(cart_id=cart_id, user=user)

    cart_item, created = Cart_item.objects.get_or_create(cart=cart, product=product, user=user)
    
    if created:
        cart_item.quantity = 1 
    else:
        cart_item.quantity += 1 
    if product.stock >= cart_item.quantity:
        product.stock -= 1
        product.save()
        cart_item.save()
    else:
        messages.info(request, f'Only {product.stock} units available in stock.')

    return redirect('cart')


def cart(request,total=0,quantity=0,cart_items=None):
    tax=0
    grand_total=0
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=Cart_item.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total=cart_item.product.price * cart_item.quantity
            quantity+=cart_item.quantity
        tax=(2*total)/100
        grand_total=tax+total
    except ObjectDoesNotExist:
        pass
    context={'total':total,'quantity':quantity,'cart_items':cart_items,'tax':tax,'grand_total':grand_total}
    return render(request,'cart/cart.html',context)

def icon_cart(request,total=0,quantity=0,cart_items=None):
    tax=0
    grand_total=0
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=Cart_item.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total=cart_item.product.price * cart_item.quantity
            quantity+=cart_item.quantity
        tax=(2*total)/100
        grand_total=tax+total
    except ObjectDoesNotExist:
        pass
    context={'total':total,'quantity':quantity,'cart_items':cart_items}
    return render(request,'header.html',context)

def clear_cart(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items =Cart_item.objects.filter(cart=cart)
    cart_items.delete()
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = Cart_item.objects.get(cart=cart, product=product)
        product.stock += cart_item.quantity
        product.save()
        cart_item.delete()

    except Cart_item.DoesNotExist:
        pass 
    return redirect('cart')



def decrement_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = Cart_item.objects.get(cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            product.stock += 1
            product.save()
        else:
            cart_item.delete()
            product.stock += 1
            product.save()
    except Cart_item.DoesNotExist:
        messages.info(request, 'Item does not exist in the cart.')
    return redirect('cart')


def increment_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_items = Cart_item.objects.filter(cart=cart, product=product)
    if cart_items.exists():
        for cart_item in cart_items:
            if product.stock <= cart_item.quantity:
                a=product.stock - cart_item.quantity
                print(a)
                messages.warning(request, f"Only {product.stock - cart_item.quantity} units of this product are available.")
                return redirect('cart')
            cart_item.quantity += 1
            cart_item.save()
            
        if len(cart_items) > 1:
            main_cart_item = cart_items.first()
            extra_cart_items = cart_items[1:]

            for extra_item in extra_cart_items:
                main_cart_item.quantity += extra_item.quantity
                extra_item.delete()
            main_cart_item.save()
        product.save()
        
    return redirect('cart')



