# Python imports
from random import randint

# Django imports
from django.db import models, IntegrityError

class PaymentManager(models.Manager):
    """
    Custom manager for payments.
    """
    def create(self, **obj_data):
        """
        Overrides the default create method. It generates a unique
        code with which the payment can be identified.
        """
        # Try creating unique code object
        while True:
            try:
                # Generate a code
                code = 'ZS1-' + randint(1000, 9999) + randint(1000, 9999)
                # Try creating token object
                obj_data['code'] = code
                payment = super().create(**obj_data)
            except IntegrityError:
                continue
            break
        return payment
