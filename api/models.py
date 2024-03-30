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
    google_auth_token = models.CharField(max_length=2000, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=[('patient', 'Patient'), ('doctor', 'Doctor')])

class Blog(models.Model):
    CATEGORY_CHOICES = [
        ('Mental Health', 'Mental Health'),
        ('Heart Disease', 'Heart Disease'),
        ('Covid19', 'Covid19'),
        ('Immunization', 'Immunization')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='blog_images/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    summary = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    draft = models.BooleanField(default=True)
