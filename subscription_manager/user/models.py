# Django imports
from django.conf import settings
from django.db.models import CharField, EmailField
from django.contrib.auth.models import AbstractUser

# Application imports
from .managers import UserManager


class User(AbstractUser):
    """
    Custom user model that inherits the AbstractUser model
    from django's default authentication application. It
    removes the username field and replaces it instead by
    the email address.
    """
    # Remove username field
    username = None
    first_name = CharField(
        max_length=30,
        verbose_name='Vorname'
    )
    last_name = CharField(
        max_length=150,
        verbose_name='Nachname'
    )
    # Make email address unique
    email = EmailField(
        unique=True,
        verbose_name='E-Mail-Adresse'
    )

    # Substitute username by email address field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return '{} ({})'.format(self.full_name(), self.email)

    def _get_email_domain(self):
        """
        Returns the user's email domain.
        """
        return self.email.split('@')[-1]
    email_domain = property(_get_email_domain)

    def _get_full_name(self):
        """
        Returns the user's full name.
        """
        return '{} {}'.format(self.first_name, self.last_name)
    full_name = property(_get_full_name)
