from datetime import timedelta
import pytz

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth import get_backends
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .managers import UserManager, LoginTokenManager


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


class LoginToken(models.Model):
    """
    Login token model.

    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    code = models.CharField(
        unique=True,
        max_length=32
    )
    valid_until = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = LoginTokenManager()

    def __str__(self):
        return 'Token({}, {})'.format(self.user.email, self.code)

    def is_valid(self):
        return timezone.now() <= self.valid_until

    def is_expired(self):
        return not self.is_valid()

    @staticmethod
    def b64_encoded(email):
        return urlsafe_base64_encode(force_bytes(email)).decode()

    @staticmethod
    def b64_decoded(email_b64):
        try:
            return force_text(urlsafe_base64_decode(email_b64))
        except DjangoUnicodeDecodeError:
            return None

    def login_url(self):
        return '{}://{}{}'.format(
            'https' if settings.USE_SSL else 'http',
            settings.HOST,
            reverse(
                'verify_token',
                kwargs={
                    'email_b64': LoginToken.b64_encoded(self.user.email),
                    'code': self.code
                }
            )
        )

    def send(self):
        for backend in get_backends():
            if hasattr(backend, 'send'):
                backend.send(self)
        self.sent_at = timezone.now()
        self.save()
