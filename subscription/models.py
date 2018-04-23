# Django imports
from django.db import models
from django.contrib.auth import get_user_model


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
        'SubscriptionType',
        on_delete=models.DO_NOTHING
    )
    shipping_address = models.ForeignKey(
        'Address',
        on_delete=models.PROTECT
    )
    billing_address = models.ForeignKey(
        'Address',
        on_delete=models.PROTECT
    )
    start_date = models.DateField()
    end_Date = models.DateField()
    created_at = models.DateTimeField()
    is_paid = models.BooleanField()
    # TODO: Payment


class SubscriptionType(models.Model):
    """
    Model that holds the information for a
    type of subscription (i.e. price).
    """
    name = models.CharField(
        max_length=50
    )
    description = models.CharField(
        max_length=500
    )
    slug = models.SlugField()
    duration = models.DurationField()
    price = models.IntegerField()
    # Whitelist for email addresses that are allowed
    # for a certain subscription type
    email_whitelist = models.CharField(
        max_length=500
    )


class Address(models.Model):
    """
    Address model.
    """
    first_name = models.CharField(
        max_length=30,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    street_1 = models.CharField(max_length=50)
    street_2 = models.CharField(
        max_length=50,
        blank=True
    )
    postcode = models.CharField(max_length=8)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
