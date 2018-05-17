# Django imports
from django.forms import ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _, ngettext

# Application imports
from .models import Payment


class PaymentForm(ModelForm):
    """
    Payment form with one input field for
    the amount.
    """
    def __init__(self, *args, **kwargs):
        # Read passed parameters
        self.price = kwargs.pop('price')
        self.fixed_price = kwargs.pop('fixed_price', True)
        # Call super constructor
        super().__init__(*args, **kwargs)
        # Create help text
        amount_help_text = ngettext(
            'Please specify a price that is greater than or equal to {} franc.',
            'Please specify a price that is greater than or equal to {} francs.',
            self.price
        ).format(self.price)
        self.fields['amount'].help_text = amount_help_text

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if self.fixed_price:
            # Check if price has the right value
            if self.price is None or amount != self.price:
                raise ValidationError(_('Wrong price.'))
        else:
            # Check whether price is high enough
            if self.price is None or amount < self.price:
                raise ValidationError(_('Price is too low.'))

        return amount

    class Meta:
        model = Payment
        fields = ('amount',)
