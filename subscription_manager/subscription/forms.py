# Django imports
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Project imports
from subscription_manager.authentication.forms import SignUpForm

# Application imports
from .models import Address, Subscription


class AddressForm(forms.ModelForm):
    """
    Address form.
    """
    country = forms.CharField(
        initial='Switzerland',
        disabled=True,
        help_text=_('We can only send our newspaper to Swiss addresses.')
    )

    class Meta:
        model = Address
        fields = ('first_name', 'last_name', 'address_line_1', 'address_line_2', 'postcode', 'city', 'country')


class AddressWithoutNamesForm(AddressForm):
    """
    Address form.
    """
    class Meta:
        model = Address
        fields = ('address_line_1', 'address_line_2', 'postcode', 'city', 'country')
