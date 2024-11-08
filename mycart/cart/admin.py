from django.contrib import admin
from .models import Cart, Cart_item
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity')

admin.site.register(Cart, CartAdmin)
admin.site.register(Cart_item, CartItemAdmin)

