from django import forms

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
        fields = ('amount', 'method')

    def __init__(self, *args, **kwargs):
        """
        Constructor. Should get two additional parameters, price (int)
        and fixed price (bool). These values are necessary for the
        validation and for generating the help text.
        """
        # Read passed parameters
        self.plan = kwargs.pop('plan', None)

        if self.plan is None:
            raise forms.ValidationError('Payment form improperly instantiated. Plan is missing.')

        # Call super constructor
        super().__init__(*args, **kwargs)

        # Add initial data
        self.fields['amount'].initial = self.plan.price

        # Add help text
        self.fields['amount'].help_text = 'Der Preis muss mindestens {} Franken betragen.'.format(self.plan.price)
        if self.plan.price == 0:
            self.fields['amount'].help_text = 'Zahle so viel du willst.'

    def clean_amount(self):
        """
        Validates whether the price is appropriate. If the price
        is fixed, the amount input has to be exactly the same as
        the given price. Otherwise, the amount input has to be
        greater than or equal to the given price.
        """
        amount = self.cleaned_data['amount']

        # Check whether price is high enough
        if amount is None or amount < self.plan.price:
            self.add_error('amount', 'Der Preis muss mindestens {} Franken betragen.'.format(self.plan.price))

        return amount
