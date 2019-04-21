# Python imports
from random import randint

# Django imports
from django.db import models, IntegrityError
from django.utils import timezone


class PaymentManager(models.Manager):
    """
    Custom manager for payments.
    """

