# Django imports
from django import forms

# Application imports
from .models import Subscription


class SubscriptionForm(forms.ModelForm):
    """
    Address form. It disables the country
    field because only Swiss addresses are supported.
    """
    country = forms.CharField(
        label='Land',
        max_length=50,
        initial='Schweiz',
        disabled=True,
        help_text='Wir können nur innerhalb der Schweiz versenden.'
    )

    required_css_class = 'required'

    class Meta:
        model = Subscription
        fields = ('address_line', 'additional_address_line', 'postcode', 'town', 'country')
