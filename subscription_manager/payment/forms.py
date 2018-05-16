# Django imports
from django.forms import ModelForm, IntegerField

# Application imports
from .models import Payment


class PaymentForm(ModelForm):
    """
    Payment form with one input field for
    the amount.
    """
    class Meta:
        model = Payment
        fields = ('amount',)
