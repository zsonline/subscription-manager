from django.db import models

from account.models import User


class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    street_1 = models.CharField(max_length=50)
    street_2 = models.CharField(max_length=50, blank=True, null=True)
    postcode = models.CharField(max_length=8)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)