# Django imports
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

# Application imports
from .models import Payment


class PaymentForm(ModelForm):
    """
    Payment form with one input field for
    the amount.
    """
    def is_valid(self, min_price=None):
        """
        Overrides default is_valid method. In addition to the
        default validations, it also checks
        """
        # Check default validations
        valid = super().is_valid()
        if not valid:
            return False

        # Check whether price is high enough
        if min_price is not None:
            if price < min_price:
                self.add_error('amount', _('Price is too low.'))
                return False

        return True

    class Meta:
        model = Payment
        fields = ('amount',)
