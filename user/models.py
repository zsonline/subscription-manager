from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import UserManager


class User(AbstractUser):
    """
    Custom user model that inherits the AbstractUser
    model from django's default authentication application.

    It removes the username field and replaces it instead by
    the email address. In order to handle the modifications,
    it uses a custom UserManager.
    """
    # Remove username and password field
    username = None

    # Substitute username by email address field
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'

    # Use custom UserManager for user creation
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return 'User({})'.format(self.email)
