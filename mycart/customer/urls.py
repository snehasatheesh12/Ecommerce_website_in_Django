from django.shortcuts import render
from django.urls import path
from customer import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('profile/', views.customer_profile_view, name='customer_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('delete_profile/',views.delete_profile,name='delete_profile'),
    path('forgot-password', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
    path('password-change-done/', lambda request: render(request, 'customer/customer_password_change_done.html'), name='password_change_done'),
    path('my-orders/', views.user_orders, name='user_orders'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)