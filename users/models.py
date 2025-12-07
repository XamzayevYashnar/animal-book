from django.db import models
from django.contrib.auth.models import AbstractUser 

# Create your models here.

# users/models.py fayliga qo'shing:
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='user_avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.username