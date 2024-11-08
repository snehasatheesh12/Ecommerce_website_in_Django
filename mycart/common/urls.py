from django.shortcuts import render
from django.urls import path
from common import views

urlpatterns = [
    path('', views.home, name='home'),
    path('seller_approve_delivery_view', views.seller_approve_delivery_view,name='seller_approve_delivery_view'),
    path('approve_delivery_view/<int:pk>', views.approve_delivery_view,name='approve_delivery_view'),
    path('reject_seller_view/<int:pk>', views.reject_seller_view,name='reject_seller_view'),
    path('seller_forgot_password', views.seller_forgot_password, name='seller_forgot_password'),
    path('seller_reset_password/<uidb64>/<token>/', views.seller_reset_password, name='seller_reset_password'),
    path('seller_password-change-done/', lambda request: render(request, 'seller/seller_password_change_done.html'), name='seller_password_change_done'),
    path('seller_change-password/', views.seller_change_password, name='seller_change_password'),
    path('about',views.about,name='about'),  
]

