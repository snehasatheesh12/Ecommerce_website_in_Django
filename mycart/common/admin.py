from django.contrib import admin
from .models import *
admin.site.register(Category)
# Register your models here.
from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'title_inner')
