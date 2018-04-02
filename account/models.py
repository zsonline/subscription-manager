from datetime import timedelta
import pytz
from secrets import token_urlsafe

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now

from . import managers


class User(AbstractUser):
    """Custom user model that inherits the AbstractUser
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
    objects = managers.UserManager()


class Token(models.Model):
    """Login token model.

    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    key = models.CharField(
        unique=True,
        max_length=32
    )
    valid_until = models.DateTimeField()
    type = models.CharField(
        max_length=20,
        choices=(
            ('verification', 'Verification token'),
            ('login', 'Login token')
        )
    )
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{2} of {1} ({0})'.format(self.key, self.user.email, self.get_type_display())

    @classmethod
    def create(cls, user, type, valid_until=None):
        if not valid_until:
            if type == 'verification':
                valid_until = now() + settings.TOKEN_EXPIRATION['VERIFICATION']
            elif type == 'login':
                valid_until = now() + settings.TOKEN_EXPIRATION['LOGIN']
        key = token_urlsafe(32)
        return cls(user=user, key=key, type=type, valid_until=valid_until)

    def is_valid(self):
        return self.valid_until <= now()

    def is_expired(self):
        return not self.is_valid()

    def generate_link(self):
        return 'http://{}{}'.format(
            settings.DOMAIN,
            reverse(
                'verify_token',
                kwargs={
                    'uid': urlsafe_base64_encode(force_bytes(self.user.id)).decode(),
                    'key': self.key
                }
            )
        )

    def save_and_send(self):
        self.save()
        self.send()

    def send(self):
        subject = '{}: {}'.format(settings.NAME, self.get_type_display())
        content = render_to_string(
            'emails/confirm_email.html',
            {
                'to_name': self.user.first_name,
                'from_name': settings.NAME,
                'link': self.generate_link()
            }
        )
        from_email = settings.EMAIL_FROM_ADDRESS
        to_email = [self.user.email]
        self.sent_at = now()
        self.save()
        send_mail(subject, content, from_email, to_email)
