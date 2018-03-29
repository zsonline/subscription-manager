from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
