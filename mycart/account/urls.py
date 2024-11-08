from django.urls import path
from account import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('seller_signup_view', views.seller_signup_view,name='seller_signup_view'),
    path('seller_login_view', views.seller_login_view,name='seller_login_view'),
    path('is_seller', views.is_seller,name='is_seller'),
    path('afterlogin_view', views.afterlogin_view,name='afterlogin_view'),
    path('seller_dashboard', views.seller_dashboard,name='seller_dashboard'),
    
    path('register/', views.register_customer, name='register_customer'),
    path('customer_login_view', views.customer_login_view,name='customer_login_view'),
    path('is_customer', views.is_customer,name='is_customer'),
    path('customer_dashboard', views.customer_dashboard,name='customer_dashboard'),
    
    path('register_delivery_boy/', views.register_delivery_boy, name='register_delivery_boy'),
    path('delivery_login_view', views.delivery_login_view,name='delivery_login_view'),
    path('is_delivery_boy', views.is_delivery_boy,name='is_delivery_boy'),
    path('logout/', views.logout_view, name='logout_view'),
    path('delivery_boy_dashboard',views.delivery_boy_dashboard,name='delivery_boy_dashboard'),
    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
    path('logins', views.logins,name='logins'),
    path('register', views.register,name='register'),
    path('handel_logout', views.handel_logout,name='handel_logout'),
    path('contact',views.contact,name='contact'),


    






]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)