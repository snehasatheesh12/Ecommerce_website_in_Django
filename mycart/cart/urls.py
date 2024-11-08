from django.urls import path
from cart import views

urlpatterns = [
    path('cart',views.cart,name='cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('decrement_item/<int:product_id>',views.decrement_item,name="decrement_item"),
    path('increment_item/<int:product_id>',views.increment_item,name="increment_item"),
    path('icon_cart',views.icon_cart,name='icon_cart'),


    ]
