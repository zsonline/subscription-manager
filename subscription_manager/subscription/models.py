# Django imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

# Project imports
from subscription_manager.payment.models import Payment

# Application imports
from .plans import Plans


class Subscription(models.Model):
    """
    Model that holds the information for a
    user's subscription.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    plan = models.CharField(
        max_length=7,
        choices=Plans.convert_to_choices()
    )
    first_name = models.CharField(
        'Vorname',
        max_length=30,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        'Nachname',
        max_length=150,
        blank=True,
        null=True
    )
    address_line_1 = models.CharField(
        'Adresse',
        max_length=50
    )
    address_line_2 = models.CharField(
        'Adresszusatz',
        max_length=50,
        blank=True,
        null=True,
    )
    postcode = models.CharField(
        'Postleitzahl',
        max_length=8,
    )
    city = models.CharField(
        'Ort',
        max_length=50
    )
    country = models.CharField(
        'Land',
        max_length=50,
        default='Schweiz'
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT
    )
    start_date = models.DateField()
    end_date = models.DateField()
    canceled_at = models.DateTimeField(
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Subscription({}, {})'.format(self.user.email, self.plan)

    def has_started(self):
        """
        True if the subscription has started.
        Otherwise false.
        """
        return self.start_date <= timezone.now().date()

    def has_ended(self):
        """
        True if the subscription has ended.
        Otherwise false.
        """
        return self.end_date <= timezone.now().date()

    def is_canceled(self):
        return self.canceled_at is not None

    def is_active(self):
        """
        Checks whether the subscription is active.
        """
        return self.payment.is_paid() and not self.is_canceled() and self.has_started() and not self.has_ended()
