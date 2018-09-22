# Pip imports
from dateutil.relativedelta import relativedelta

# Django imports
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

# Application imports
from .managers import SubscriptionManager


class Subscription(models.Model):
    """
    Model that holds the information for a
    user's subscription.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    plan = models.ForeignKey(
        'Plan',
        on_delete=models.PROTECT,
        verbose_name='Abo-Typ'
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
    start_date = models.DateField(
        null=True
    )
    end_date = models.DateField(
        null=True
    )
    canceled_at = models.DateTimeField(
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Custom model manager
    objects = SubscriptionManager()

    def __str__(self):
        return 'Subscription({}, {})'.format(self.user.email, self.plan)

    def has_started(self):
        """
        True if the subscription has started.
        Otherwise false.
        """
        return self.start_date is not None and self.start_date <= timezone.now().date()

    def has_ended(self):
        """
        True if the subscription has ended.
        Otherwise false.
        """
        return self.end_date is not None and self.end_date <= timezone.now().date()

    def is_canceled(self):
        """
        Returns true if the canceled_at field
        is set.
        """
        return self.canceled_at is not None

    def is_active(self):
        """
        Checks whether the subscription is active.
        """
        return not self.is_canceled() and self.has_started() and not self.has_ended()

    def renew(self):
        """
        Renews the subscription by the duration of the
        plan.
        """
        self.end_date += relativedelta(months=+self.plan.duration)
        self.save()
        return self

    def has_open_payments(self):
        """
        Returns true if at least one payment associated with
        this subscription is open. Otherwise false.
        """
        payments = self.payment_set.all()
        if payments is None:
            return False
        for payment in payments:
            if not payment.is_paid():
                return True
        return False


class Plan(models.Model):
    """
    Model that holds the information for a
    type of subscription (i.e. price).
    """
    name = models.CharField(
        'Name',
        max_length=50
    )
    description = models.TextField(
        'Beschreibung'
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )
    duration = models.PositiveSmallIntegerField(
        'Laufzeit',
        default=12,
        help_text='Laufzeit in Monaten'
    )  # In months
    price = models.PositiveSmallIntegerField(
        'Preis'
    )

    def __str__(self):
        return 'Plan({})'.format(self.name)
