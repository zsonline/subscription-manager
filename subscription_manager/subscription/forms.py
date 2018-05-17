# Django imports
from django.forms import ModelForm, CharField
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Application imports
from .models import Address


class AddressForm(ModelForm):
    """
    Address form.
    """
    country = CharField(
        initial='Switzerland',
        disabled=True,
        help_text=_('We can send our newspaper only to Swiss addresses.')
    )

    required_css_class = 'required'

    class Meta:
        model = Address
        fields = ('first_name', 'last_name', 'address_line_1', 'address_line_2', 'postcode', 'city', 'country')


class AddressWithoutNamesForm(AddressForm):
    """
    Address form.
    """
    required_css_class = 'required'

    class Meta:
        model = Address
        fields = ('address_line_1', 'address_line_2', 'postcode', 'city', 'country')
