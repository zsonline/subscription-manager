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
    class Meta:
        model = Address
        fields = ('first_name', 'last_name', 'street_1', 'street_2', 'postcode', 'city')


class AddressWithoutNamesForm(forms.ModelForm):
    """
    Address form.
    """
    class Meta:
        model = Address
        fields = ('street_1', 'street_2', 'postcode', 'city')
