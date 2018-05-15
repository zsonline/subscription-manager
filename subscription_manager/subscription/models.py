# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Project imports
from subscription_manager.payment.models import Payment


class SubscriptionType(models.Model):
    """
    Model that holds the information for a
    type of subscription (i.e. price).
    """
    name = models.CharField(
        max_length=50
    )
    description = models.TextField()
    slug = models.SlugField(
        unique=True,
        help_text=_('Unique identifier for this subscription type.')
    )
    duration = models.DurationField(
        help_text=_('Specify a duration in the format \"years:months:days\".')
    )
    fixed_price = models.BooleanField(
        default=True,
        help_text=_('If False, users can choose a value greater or equal than the set price.')
    )
    price = models.PositiveSmallIntegerField(
        help_text=_('Price in CHF for the duration.'),
    )
    allow_other_name = models.BooleanField(
        default=False,
        help_text=_('If True, the user can purchase a subscription for someone other than herself.')
    )

    def __str__(self):
        return 'SubscriptionType({})'.format(self.name)



class Subscription(models.Model):
    """
    Model that holds the information for a
    user's subscription.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        SubscriptionType,
        on_delete=models.DO_NOTHING
    )
    address = models.ForeignKey(
        'Address',
        on_delete=models.PROTECT,
        related_name='shipping_address'
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.DO_NOTHING
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Subscription({}, {}, {}, {})'\
            .format(self.user.email, self.type.name, self.address.address_line_1, self.address.city)

    def end_date(self):
        """
        Returns duration of the subscription.
        """
        return self.start_date + self.type.duration

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
        max_length=30,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    address_line_1 = models.CharField(
        max_length=50,
        verbose_name=_('Address line')
    )
    address_line_2 = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    postcode = models.CharField(max_length=8)
    city = models.CharField(max_length=50)
    country = models.CharField(
        max_length=50,
        default='Switzerland'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Address({}, {})'.format(self.address_line_1, self.city)
