# Django imports
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    amount = models.IntegerField()
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

    def __str__(self):
        return 'Payment({}, {}, {})'.format(self.subscription.user.name, self.amount, self.paid_at)

    def is_paid(self):
        return self.paid_at is not None

    def status(self):
        if self.is_paid():
            return _('paid')
        return _('not paid')
