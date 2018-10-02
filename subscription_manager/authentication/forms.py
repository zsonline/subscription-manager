# Django imports
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings

# Application imports
from .models import Token


class SignUpForm(forms.ModelForm):
    """
    Sign up form. Allows a user to sign up with
    his email address, first name and last name.
    """
    required_css_class = 'required'

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')
        error_messages = {
            'email': {
                'unique': 'Ein Account mit dieser E-Mail-Adresse existiert bereits. Versuche dich stattdessen anzumelden.'
            }
        }

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
    email = forms.EmailField()

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
            user = get_user_model().objects.get(email=self.cleaned_data['email'])
        except get_user_model().DoesNotExist:
            # Add error if user does not exist
            self.add_error(None, 'Der Account {} existiert nicht.'.format(self.cleaned_data['email']))
            return False

        if not user.is_active:
            self.add_error(None, 'Der Account {} ist gesperrt.'.format(self.cleaned_data['email']))
            return False

        if Token.objects.valid_user_tokens_count(user) >= settings.TOKENS_PER_USER:
            self.add_error(
                None,
                'Du hast bereits die maximale Anzahl an Tokens angefordert. '
                'Warte zehn Minuten, bevor du es erneut probierst.'
                .format(self.cleaned_data['email'])
            )
            return False

        return True
