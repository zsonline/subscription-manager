# Django imports
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    amount = models.IntegerField()
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_paid(self):
        return self.paid_at is not None

    def status(self):
        if self.is_paid():
            return _('paid')
        return _('not paid')
