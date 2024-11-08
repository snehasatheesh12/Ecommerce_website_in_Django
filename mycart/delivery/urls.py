from django.shortcuts import render
from django.urls import path
from delivery import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('edit_profile_delivery',views.edit_profile_delivery,name='edit_profile_delivery'),
    path('delivery_profile_view',views.delivery_profile_view,name='delivery_profile_view'),
    path('delete_profile_delivery',views.delete_profile_delivery,name='delete_profile_delivery'),
    path('delivery_forgot_password', views.delivery_forgot_password, name='delivery_forgot_password'),
    path('delivery_reset_password/<uidb64>/<token>/', views.delivery_reset_password, name='delivery_reset_password'),
    path('delivery_password-change-done/', lambda request: render(request, 'delivery/delivery_password_change_done.html'), name='delivery_password_change_done'),
    path('delivery_change-password/', views.delivery_change_password, name='delivery_change_password'),
    path('delivery_boy/orders/', views.delivery_boy_orders, name='delivery_boy_orders'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)