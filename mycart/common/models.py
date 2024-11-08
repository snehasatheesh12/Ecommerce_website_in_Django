from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.SlugField(max_length=100,unique=True)
    description=models.TextField(max_length=225,blank=True)
    cat_image=models.ImageField(upload_to='media/categories',blank=True)
    
    
    class Meta:
        verbose_name='category'
        verbose_name_plural='categories'
        
    def get_url(self):
         return reverse('product_by_category',args=[self.slug])
        
    def __str__(self):
       return self.category_name
   

from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    title_inner = models.CharField(max_length=100, help_text="Inner title or organization name")
    image = models.ImageField(upload_to='testimonials/')  # Assuming you'll store images in a directory named 'testimonials'

    def __str__(self):
        return self.name
