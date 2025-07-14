from django.db import models
from django.contrib.auth.models import AbstractUser

#   This custom user model extends Django's AbstractUser to include an additional 'user_type' field.
#   It allows the application to distinguish between different user roles (e.g., customer vs venue admin).
#   Useful for implementing role-based permissions, views, or logic across the app.
#   The 'choices' attribute ensures valid role selection, and the __str__ method helps in admin readability.

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('venue_admin', 'Venue Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.user_type})"
    

