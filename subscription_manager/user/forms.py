from django import forms
from django.conf import settings

from .models import EmailAddress, User, Token


class SignUpForm(forms.ModelForm):
    """
    Sign up form. Allows a user to sign up with
    his email address, first name and last name.
    """
    required_css_class = 'required'

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        error_messages = {
            'email': {
                'unique': 'Ein Account mit dieser E-Mail-Adresse existiert bereits.'
            }
        }

    def clean_email(self):
        """
        Checks if the given email is allowed to purchase
        the selected subscription plan.
        """
        email = self.cleaned_data['email']

        if EmailAddress.objects.filter(email=email).exists():
            self.add_error('email', 'Ein Account mit dieser E-Mail-Adresse existiert bereits.')

        return email

    def save(self, commit=True):
        """
        Custom save method that saves newly registered
        users with an unusable password.
        """
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Login form. Allows a user to log himself in.
    A token is afterwards sent to her email address.
    """
    email = forms.EmailField(required=True)

    required_css_class = 'required'

    def is_valid(self):
        """
        Overrides default is_valid method. In addition to the
        default validations, it also checks whether a user
        for a given email address exists and adds an error if
        it does not.
        """
        # Check default validations
        valid = super().is_valid()
        if not valid:
            return False

        # Check whether user exists
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            # Add error if user does not exist
            self.add_error(None, 'Der Account existiert nicht.')
            return False

        if not user.is_active:
            self.add_error(None, 'Der Account ist gesperrt.')
            return False

        if Token.objects.count_created_in_last_hour(user, 'login') >= settings.TOKENS_PER_USER_PER_HOUR:
            self.add_error(None, 'Du hast die maximale Anzahl an Tokens erreicht. Warte eine Stunde, bevor du es erneut probierst.')
            return False

        return True
