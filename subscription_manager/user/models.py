from django.conf import settings
from django.db.models import CharField, EmailField
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

    # Model fields
    first_name = CharField(
        'Vorname',
        max_length=30
    )
    last_name = CharField(
        'Nachname',
        max_length=150
    )
    # Make email address unique
    email = EmailField(
        'E-Mail-Adresse',
        unique=True
    )

    # Substitute username by email address field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    # Use custom UserManager for user creation
    objects = UserManager()

    def __str__(self):
        return 'User({})'.format(self.email)

    def is_student(self):
        """
        Checks whether the user has a student email address.
        """
        # Extract domain from email address
        email_domain = self.email.split('@')[1]
        # Check if extracted domain is in list
        if email_domain in settings.ALLOWED_STUDENT_EMAIL_ADDRESSES:
            return True
        return False
