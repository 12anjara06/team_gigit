from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    face_encoding = models.JSONField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    def __str__(self):
        return self.username
