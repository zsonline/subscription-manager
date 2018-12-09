from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings

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
                'unique': 'Ein Account mit dieser E-Mail-Adresse existiert bereits.'
            }
        }

    def __init__(self, *args, **kwargs):
        """
        Constructor. Should get the selected plan. The plan is
        necessary for the validation.
        """
        # Read passed parameters
        self.plan = kwargs.pop('plan', None)

        if self.plan is None:
            raise forms.ValidationError('Sign up form improperly instantiated. Plan is missing.')

        # Call super constructor
        super().__init__(*args, **kwargs)

        if self.plan.get_eligible_email_domains():
            # Add help text
            self.fields['email'].help_text = \
                'Die E-Mail-Adresse muss auf {} enden.'.format(self.plan.get_readable_eligible_email_domains('oder'))

    def clean_email(self):
        """
        Checks if the given email is allowed to purchase
        the selected subscription plan.
        """
        email = self.cleaned_data['email']

        if self.plan.get_eligible_email_domains():
            # Extract email domain from email address
            email_domain = email.split('@')[-1]
            # Check if extracted domain is in list
            if email_domain not in self.plan.get_eligible_email_domains():
                self.add_error('email', 'Deine E-Mail-Adresse muss auf {} enden.'
                               .format(self.plan.get_readable_eligible_email_domains('oder')))

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
