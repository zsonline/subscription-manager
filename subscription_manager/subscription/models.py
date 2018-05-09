# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Project imports
from subscription_manager.payment.models import Payment


class Subscription(models.Model):
    """
    Model that holds the information for a
    user's subscription.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    type = models.CharField(
        max_length=7,
        choices=(
            ('regular', _('Regular')),
            ('student', _('Student')),
            ('gift', _('Gift'))
        )
    )
    shipping_address = models.ForeignKey(
        'Address',
        on_delete=models.PROTECT,
        related_name='shipping_address'
    )
    billing_address = models.ForeignKey(
        'Address',
        on_delete=models.PROTECT,
        related_name='billing_address'
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.DO_NOTHING
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def duration(self):
        """
        Returns duration of the subscription.
        """
        return self.end_date - self.start_date

    def has_started(self):
        """
        True if the subscription has started.
        Otherwise false.
        """
        return self.start_date <= timezone.now()

    def has_ended(self):
        """
        True if the subscription has ended.
        Otherwise false.
        """
        return self.end_date <= timezone.now()

    def is_active(self):
        """
        Checks whether the subscription is active.
        """
        return self.has_started() and not self.has_ended()

    def status(self):
        """
        Returns status of the subscription.
        Does not check the payment status.
        """
        if not self.has_started():
            return _('inactive')
        if self.is_active():
            return _('active')
        if self.has_ended():
            return _('expired')


class Address(models.Model):
    """
    Address model.
    """
    first_name = models.CharField(
        max_length=30
    )
    last_name = models.CharField(
        max_length=150
    )
    street_1 = models.CharField(max_length=50)
    street_2 = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    postcode = models.CharField(max_length=8)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
