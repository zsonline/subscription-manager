from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(forms.ModelForm):

    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def send(self):
        pass

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_unusable_password()
        user.is_active = False
        user.save()
        return user


class SignInForm(forms.ModelForm):

    email = forms.EmailField()
