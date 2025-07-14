from django import forms
from django.contrib.auth.forms import UserCreationForm 
from .models import CustomUser

#   This form extends Django's built-in UserCreationForm to support the CustomUser model.
#   It is used during user registration to collect necessary fields:
#   username, email, user type, and password (with confirmation).
#   By linking to CustomUser, it allows saving extra user info (e.g., user_type) during sign-up.
#   Django automatically handles password validation and user creation through this form.


class CustomUserCreationForm(UserCreationForm): 
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'password1', 'password2')
        