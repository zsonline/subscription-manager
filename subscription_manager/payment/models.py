# Python imports
from datetime import timedelta

# Django imports
from django.db import models

# Application imports
from .managers import PaymentManager


class Payment(models.Model):
    amount = models.IntegerField(
        'Betrag'
    )
    code = models.CharField(
        max_length=30,
        unique=True
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()

    def __str__(self):
        return 'Payment({}, {}, {})'.format(self.subscription.user.email, self.amount, self.paid_at)

    def is_paid(self):
        return self.paid_at is not None

    def pay_until(self):
        return (self.created_at + timedelta(days=30)).date()
