from django.contrib import admin
from .models import *
admin.site.register(Order)
# Register your models here.
admin.site.register(Payment)
admin.site.register(OrderProduct)
