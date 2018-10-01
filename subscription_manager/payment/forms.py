# Python imports
from random import randint

# Django imports
from django import forms
from django.db import IntegrityError

# Application imports
from .models import Payment


class PaymentForm(forms.ModelForm):
    """
    Payment model form with one input field for the amount.
    Has custom validation that checks whether the price is
    correct.
    """
    required_css_class = 'required'

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
        self.min_price = kwargs.pop('min_price', None)

        if self.min_price is None:
            raise forms.ValidationError('Payment form improperly instantiated.')

        # Call super constructor
        super().__init__(*args, **kwargs)

        # Add help text
        self.fields['amount'].help_text = \
            'Der Preis muss mindestens {} Franken betragen.'.format(self.min_price)
        if self.min_price == 0:
            self.fields['amount'].help_text = \
                'Zahl so viel du willst.'.format(self.min_price)


    def clean_amount(self):
        """
        Validates whether the price is appropriate. If the price
        is fixed, the amount input has to be exactly the same as
        the given price. Otherwise, the amount input has to be
        greater than or equal to the given price.
        """
        amount = self.cleaned_data['amount']

        # Check whether price is high enough
        if amount is None or amount < self.min_price:
            self.add_error('amount', 'Der Preis muss mindestens {} Franken betragen.'.format(self.min_price))

        return amount

    def save(self, commit=True):
        """
        Overrides the default save method. It generates
        and saves a unique payment code.
        """
        # Default method
        payment = super().save(commit=False)
        # Try creating unique code object
        while True:
            try:
                # Generate a code
                code = 'ZS1-' + str(randint(1000, 9999)) + '-' + str(randint(1000, 9999))
                payment.code = code
                if commit:
                    payment.save()
            except IntegrityError:
                continue
            break
        return payment
