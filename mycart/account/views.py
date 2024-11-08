import threading
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View

from cart.models import Cart, Cart_item
from cart.views import _cart_id
from order.models import Order
from store.models import Product
from .models import CustomerProfile
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate

from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .models import DeliveryBoy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
import json
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.urls import NoReverseMatch,reverse
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.mail import BadHeaderError,send_mail
from django.core import mail
from django.conf import settings
from .utils import TokenGenerator,generate_token
import uuid  
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import *
def logins(request):
    return render(request,'login.html')

def register(request):
    return render(request,'register.html')


@csrf_exempt
def register_customer(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        gender = request.POST.get('gender')
        profile_pic = request.FILES.get('profile_pic')
        repassword=request.POST.get('repassword')
        if password==repassword:
            if User.objects.filter(username=username).exists():
                    messages.error(request, 'username exist')
            elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email exist')
            user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username, password=password, email=email)
            customer=CustomerProfile.objects.create(
                user=user,
                phone_number=phone_number,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                gender=gender,
                profile_pic=profile_pic
            )    
            customer.save()
            customer_group = Group.objects.get_or_create(name='CUSTOMER')
            customer_group[0].user_set.add(user)
            mail_subject='please activate your account'
            current_site=get_current_site(request)
            message=render_to_string('account_verification.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':generate_token.make_token(user)})
            to_email=email
            send_email=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER,[to_email])
            EmailThread(send_email).start()
            messages.success(request, 'Account created successfully! Please check your email for activate the account .')           
        else:
            messages.success(request, 'please..check registration is failed')           
    return render(request, 'customer/register_customer.html')

def customer_login_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='CUSTOMER').exists():
            return HttpResponseRedirect('customer_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                cart_id = _cart_id(request)
                cart, created = Cart.objects.get_or_create(cart_id=cart_id, defaults={'user': user})

                if created:
                    print("Created new cart for user.")
                else:
                    print(f"Cart {cart_id} already exists for user.")
                cart_items = Cart_item.objects.filter(cart=cart)
                if cart_items.exists():
                    print(f"Found {cart_items.count()} items in the cart.")
                    for item in cart_items:
                        item.user = user
                        item.save()
                        print(f"Updated cart item {item.id} for user {user.username}")
                else:
                    print("No cart items found for this session.")
            except Cart.DoesNotExist:
                print("Cart does not exist for this session.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            if user.groups.filter(name='CUSTOMER').exists():
                login(request, user)
                current_user = CustomerProfile.objects.get(user__id=request.user.id)
                saved_cart = current_user.old_cart  
                
                if saved_cart:  
                    try:
                        parsed_cart = json.loads(saved_cart)  

                        for product_id, quantity in parsed_cart.items():
                            product = Product.objects.get(id=product_id)  
                            cart_item, created = Cart_item.objects.get_or_create(
                                product=product,
                                user=user,
                                cart=cart  
                            )
                            if created:
                                cart_item.quantity = quantity
                            else:
                                cart_item.quantity += quantity
                            cart_item.save()
                    except json.JSONDecodeError:
                        print("Failed to decode old_cart JSON. It might be empty or invalid.")

                return redirect('afterlogin_view')
            else:
                messages.error(request, 'You do not have valid credentials.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'customer/login_customer.html')


# @login_required(login_url='customer_login_view')
# def checkout(request):
#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#         cart_items = cart.cart_item_set.all()

#         total_amount = sum(item.product.price * item.quantity for item in cart_items)

#         if request.method == 'POST':
#             order = Order.objects.create(user=request.user, total_amount=total_amount)

#             for item in cart_items:
#                 order.order_items.create(
#                     product=item.product,
#                     quantity=item.quantity,
#                     price=item.product.price,
#                 )


#             return redirect('order_success')  

#         return render(request, 'cart/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})

#     except Cart.DoesNotExist:
#         return redirect('shop')


def seller_signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if password==repassword:
            if User.objects.filter(username=username).exists():
                    messages.error(request, 'username exist')
            elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email exist')

            user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
            user.set_password(password)
            user.save()

            my_admin_group, created = Group.objects.get_or_create(name='SELLER')
            my_admin_group.user_set.add(user)
            mail_subject='please activate your account'
            current_site=get_current_site(request)
            message=render_to_string('account_verification.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':generate_token.make_token(user)})
            to_email=email
            send_email=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER,[to_email])
            EmailThread(send_email).start()
            messages.success(request, 'Account created successfully! Please check your email for activate the account .')   

            return HttpResponseRedirect('seller_login_view')
        else:
            messages.error(request, 'password donot match')
    return render(request, 'seller/seller-signup.html')


def seller_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.groups.filter(name='SELLER').exists():
            return HttpResponseRedirect('seller_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff and user.groups.filter(name='SELLER').exists():
                login(request, user)
                return redirect('afterlogin_view')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'seller/seller-login.html')


def logout_view(request):
    if request.user.is_authenticated:
        cart_id = _cart_id(request)
        cart_items = Cart_item.objects.filter(cart__cart_id=cart_id)
        cart_data = {}

        for item in cart_items:
            cart_data[item.product.id] = item.quantity

        cart_json = json.dumps(cart_data)
        
        try:
            current_user = CustomerProfile.objects.get(user=request.user)
            current_user.old_cart = cart_json
            current_user.save()
        except CustomerProfile.DoesNotExist:
            pass  
        logout(request)
    
    return redirect('home') 
    
@csrf_exempt
def register_delivery_boy(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        vehicle_number = request.POST.get('vehicle_number')
        gender = request.POST.get('gender')
        profile_pic = request.FILES.get('profile_pic')
        if password==confirm_password:
            if User.objects.filter(username=username).exists():
                    messages.error(request, 'username exist')
            elif User.objects.filter(email=email).exists():
                    messages.error(request, 'Email exist')
            user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username, password=password, email=email)
            customer=DeliveryBoy.objects.create(
                user=user,
                phone_number=phone_number,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                vehicle_number=vehicle_number,
                gender=gender,
                profile_pic=profile_pic,
            )    
            customer.save()
            customer_group = Group.objects.get_or_create(name='DELIVERY')
            customer_group[0].user_set.add(user)
            mail_subject='please activate your account'
            current_site=get_current_site(request)
            message=render_to_string('account_verification.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':generate_token.make_token(user)})
            to_email=email
            send_email=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER,[to_email])
            EmailThread(send_email).start()
            messages.success(request, 'Account created successfully! Please check your email for activate the account .')   
            return redirect('delivery_login_view') 
        else:
            messages.error(request, 'password donot match')
    return render(request, 'delivery/register_delivery_boy.html')

class EmailThread(threading.Thread):
    def __init__(self, send_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.send_email = send_email
        
    def run(self):
        self.send_email.send()


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            if user.groups.filter(name='SELLER').exists():
                messages.success(request, ' account activated successfully!')
                return redirect('seller_login_view')  
            elif user.groups.filter(name='CUSTOMER').exists():
                messages.success(request, ' account activated successfully!')
                return redirect('customer_login_view')  
            elif user.groups.filter(name='DELIVERY').exists(): 
                messages.success(request, ' account activated successfully!')
                return redirect('delivery_login_view')  
        else:
            messages.error(request, 'Activation link is invalid or has expired.')
        return render(request, 'account_verification.html')


def delivery_login_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='DELIVERY').exists():
            return HttpResponseRedirect('delivery_boy_dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if  user.groups.filter(name='DELIVERY').exists():
                login(request, user)
                return redirect('afterlogin_view')
            else:
                messages.error(request, 'invalid credintials')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'delivery/delivery_login.html')

def is_delivery_boy(user):
    return user.groups.filter(name='DELIVERY').exists()

def is_seller(user):
    return user.groups.filter(name='SELLER').exists()

def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

def afterlogin_view(request):
    if is_seller(request.user):
        return redirect('seller_dashboard')
    elif is_customer(request.user):
         if CustomerProfile.objects.filter(user_id=request.user.id).first():
                return redirect('customer_profile')
    elif is_delivery_boy(request.user):
        delivery = DeliveryBoy.objects.filter(user_id=request.user.id).first()
        print(delivery)
        if delivery and delivery.status:  
            return redirect('delivery_profile_view')
        else:
            return render(request, 'delivery/delivery_wait_for_approval.html')
    else:
        return redirect('home')
   
def customer_dashboard(request):
    return render(request,'customer/customer_profile_view.html')

def seller_dashboard(request):
    return render(request,'seller/seller-dashboard.html')

def delivery_boy_dashboard(request):
        return render(request,'delivery/delivery-dashboard.html')
    

def handel_logout(request):
    if request.user.is_authenticated:
        cart_id = _cart_id(request)
        cart_items = Cart_item.objects.filter(cart__cart_id=cart_id)
        cart_data = {}

        for item in cart_items:
            cart_data[item.product.id] = item.quantity

        cart_json = json.dumps(cart_data)
        try:
            current_user = CustomerProfile.objects.get(user=request.user)
            current_user.old_cart = cart_json
            current_user.save()
        except CustomerProfile.DoesNotExist:
            pass  
        logout(request)
        if request.user.groups.filter(name='CUSTOMER').exists():
            return redirect('customer_login')  
        elif request.user.groups.filter(name='DELIVERY').exists():
            return redirect('delivery_boy_login')  
    else:
        return redirect('home')  
    return render(request,'home.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('msg')

        m=Contact.objects.create(name=name, email=email, desc=message, subject=subject)
        m.save()

        from_email = settings.EMAIL_HOST_USER

        email_message = mail.EmailMessage(
            subject=f'Email is from {name}',
            body=f'User Email: {email}\nUser Phone: {phone}\n\n\nQuery:\n{message}',
            from_email=from_email,
            to=['snehasatheesh176@gmail.com']  
        )
        # email_client = mail.EmailMessage(
        #     subject=f'Email is from {name}',
        #     body=f'User Email: {email}\nUser Phone: {phone}\n\n\nQuery:\n{message}',
        #     from_email=from_email,
        #     to=['snehasatheesh176@gmail.com']  
        # )
        try:
            email_message.send()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        except Exception as e:
            messages.error(request, f'An error occurred while sending the email: {e}')
        return render(request, 'contact.html')
    return render(request, 'contact.html')