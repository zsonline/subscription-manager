# Django imports
from django import forms

# Application imports
from .plans import Plans
from .models import Subscription


class SubscriptionBaseForm(forms.ModelForm):
    """
    Address base form. It disables the country
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
        fields = ('first_name', 'last_name', 'address_line_1', 'address_line_2', 'postcode', 'city', 'country')


class SubscriptionWithNamesForm(SubscriptionBaseForm):
    """
    Address form that is similar to the base form
    but requires first and last name.
    """
    # Require names
    first_name = forms.CharField(
        label='Vorname',
        max_length=30,
        required=True)
    last_name = forms.CharField(
        label='Nachname',
        max_length=150,
        required=True
    )


class SubscriptionWithoutNamesForm(SubscriptionBaseForm):
    """
    Address form that does not include first and
    last name.
    """
    class Meta:
        model = Subscription
        fields = ('address_line_1', 'address_line_2', 'postcode', 'city', 'country')
