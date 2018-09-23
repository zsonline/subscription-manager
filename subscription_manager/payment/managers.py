# Django imports
from django.db import models, IntegrityError
from django.utils.crypto import get_random_string


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
                code = 'zs-' + obj_data['subscription'].slug + '-' + get_random_string(12)
                print(code)
                # Try creating token object
                obj_data['code'] = code
                payment = super().create(**obj_data)
            except IntegrityError:
                continue
            break
        return payment
