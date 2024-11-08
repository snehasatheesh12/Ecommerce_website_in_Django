from django.shortcuts import render

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from account.models import DeliveryBoy
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from order.models import *


@login_required
def delivery_profile_view(request):
    delivery_profile = get_object_or_404(DeliveryBoy, user=request.user)
    return render(request, 'delivery/delivery_profile_view.html', {'profile': delivery_profile})


@login_required
def edit_profile_delivery(request):
    profile = get_object_or_404(DeliveryBoy, user=request.user)
    user=request.user

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('postal_code')
        gender = request.POST.get('gender')
        vehicle_number=request.POST.get('vehicle_number')

        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']

        profile.phone_number = phone_number
        profile.address = address
        profile.city = city
        profile.state = state
        profile.postal_code = zip_code
        profile.gender = gender
        profile.vehicle_number=vehicle_number
        profile.save()
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return redirect('delivery_profile_view')  
    return render(request, 'delivery/delivery_edit_profile.html', {'profile': profile})


@login_required
def delete_profile_delivery(request):
    profile = get_object_or_404(DeliveryBoy, user=request.user)
    if request.method == 'POST':
        user = request.user
        user.delete()  
        logout(request)  
        return redirect('home')  

    return render(request, 'delivery/delete_profile.html', {'profile': profile})


def delivery_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('delivery_reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Password Reset Request'
            message = render_to_string('delivery/delivery_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            try:
                send_mail(subject, message, 'snehasatheesh176@gmail.com', [user.email])
                messages.success(request, 'Password reset link has been sent to your email.')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')
            return redirect('delivery_forgot_password')
        else:
            messages.error(request, 'No account found with that email.')
    
    return render(request, 'delivery/delivery_forgot_password.html')



def delivery_reset_password(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST['password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been reset successfully. You can now log in with your new password.')
            return redirect('delivery_login_view')  
        return render(request, 'delivery/delivery_reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'The link is invalid or has expired.')
        return redirect('delivery_forgot_password')
        
@login_required
def delivery_change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        if not check_password(old_password, user.password):
            messages.error(request, 'Old password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'The new passwords do not match.')
        elif not new_password1:
            messages.error(request, 'The new password cannot be empty.')
        else:
            user.set_password(new_password1)
            user.save()

            update_session_auth_hash(request, user)

            messages.success(request, 'Your password was successfully updated!')
            return redirect('delivery_password_change_done')

    return render(request, 'delivery/delivery_password_change.html')


@login_required
def delivery_boy_orders(request):
    delivery_boy = request.user.deliveryboy
    orders = Order.objects.filter(delivery_boy=delivery_boy)
    context = {
        'orders': orders,
    }
    return render(request, 'delivery/view_order.html', context)

# def search_here(request):
#     serach_var=products.objects.filter(category.category_name='ntri')