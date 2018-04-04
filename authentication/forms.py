from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_unusable_password()
        user.save()
        return user


class LoginForm(forms.Form):

    email = forms.EmailField()


class TokenForm(forms.Form):

    email = forms.EmailField()
    code = forms.CharField()
