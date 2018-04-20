# Django imports
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Application imports
from .models import LoginToken


class SignUpForm(forms.ModelForm):
    """
    Sign up form. Allows a user to sign up with
    his email address, first name and last name.
    """
    # ModelForm generates form fields
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name')


class LoginForm(forms.Form):
    """
    Login form. Allows a user to log himself in.
    A token is afterwards sent to her email address.
    """
    # Form fields
    email = forms.EmailField()

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
            self.add_error('email', _('User does not exist.'))
            return False

        if not user.is_active:
            return False

        if LoginToken.objects.valid_user_tokens_count(user) >= settings.MAX_TOKEN_PER_USER:
            self.add_error('email', _('You reached the maximum of allowed tokens. '
                                      'Please wait 10 minutes before you try it again.'))
            return False

        return True
