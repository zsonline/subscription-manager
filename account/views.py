from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from . import forms, models
from .models import Token

def signup(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save()
            # Create and send token
            token = Token.create(user, 'verification')
            token.save_and_send()
            return HttpResponse('Please confirm your email address.')
    else:
        form = forms.SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


def signin(request):
    if request.method == 'POST':
        form = forms.SignInForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save()
            # Create and send token
            token = Token.create(user, 'verification')
            token.save_and_send()
            return HttpResponse('Please confirm your email address.')
    else:
        form = forms.SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})

def verify_token(request, uid, key):
    token = Token.objects.get(key=key)
    if token:
        user_id = force_text(urlsafe_base64_decode(uid))
        user = authenticate(user_id=user_id, key=key)
        if user is not None:
            if token.type == 'login':
                login(request, user)
                return HttpResponse('Login successful')
            elif type == 'verification':
                user.is_active = True
                user.save()
                login(request, user)
                return HttpResponse('Verification successful')
    return HttpResponse('Invalid token')

def logout(request):
    pass

def home(request):
    pass