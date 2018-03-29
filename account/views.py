from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate

from . import forms


def signup(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            form.save()

            return HttpResponse(form)
    else:
        form = forms.SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})
