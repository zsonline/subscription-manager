# Django imports
from django.forms import ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _, ngettext

# Application imports
from .models import Payment


class PaymentForm(ModelForm):
    """
    Payment model form with one input field for the amount.
    Has custom validation that checks whether the price is
    correct.
    """
    class Meta:
        model = Payment
        fields = ('amount',)

    def __init__(self, *args, **kwargs):
        """
        Constructor. Should get two additional parameters, price (int)
        and fixed price (bool). These values are necessary for the
        validation and for generating the help text.
        """
        # Read passed parameters
        self.price = kwargs.pop('price', None)
        if self.price is None:
            raise ValidationError(_('Payment form improperly instantiated. Price is missing.'))
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
        """
        Validates whether the price is appropriate. If the price
        is fixed, the amount input has to be exactly the same as
        the given price. Otherwise, the amount input has to be
        greater than or equal to the given price.
        """
        amount = self.cleaned_data['amount']

        if self.fixed_price:
            # Check if price has the right value
            if self.price is None or amount != self.price:
                error = ngettext(
                    'The price has to be exactly {} franc.',
                    'The price has to be exactly {} francs.',
                    self.price
                ).format(self.price)
                self.add_error('amount', error)
        else:
            # Check whether price is high enough
            if self.price is None or amount < self.price:
                error = ngettext(
                    'The price has to be greater than or equal to {} franc.',
                    'The price has to be greater than or equal to {} francs.',
                    self.price
                ).format(self.price)
                self.add_error('amount', error)

        return amount
