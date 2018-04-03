from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(forms.ModelForm):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'First name',
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
            }
        )
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def send(self):
        pass

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_unusable_password()
        user.save()
        return user


class LoginForm(forms.Form):

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }
        )
    )


class TokenForm(forms.Form):

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }
        )
    )
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Key',
            }
        )
    )
