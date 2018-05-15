# Django imports
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Project imports
from subscription_manager.authentication.forms import SignUpForm

# Application imports
from .models import Address, Subscription


class SubscribeForm(forms.ModelForm):
    """
    Subscription form.
    """
    type = forms.ChoiceField(
        choices=(
            ('regular', _('Regular')),
            ('student', _('Student'))
        ),
        widget=forms.RadioSelect()
    )

    # ModelForm generates form fields
    class Meta:
        model = Subscription
        fields = ('type',)


class AddressForm(forms.ModelForm):
    """
    Address form.
    """
    class Meta:
        model = Address
        exclude = ('country', 'created_at')
