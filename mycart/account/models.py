from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    profile_pic=models.FileField(upload_to='media/customer')
    old_cart=models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        return self.user.username

class DeliveryBoy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    status= models.BooleanField(default=False)
    profile_pic=models.FileField(upload_to='media/delivery')
    
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.phone_number})"


class Contact(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    desc=models.TextField()
    subject=models.CharField(max_length=100)