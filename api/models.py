from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/')
    line = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    pincode = models.CharField(max_length=6)
    user_type = models.CharField(max_length=10, choices=[('patient', 'Patient'), ('doctor', 'Doctor')])