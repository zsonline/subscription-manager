from datetime import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail

from . import managers


class User(AbstractUser):
    """Custom user model that inherits the AbstractUser
    model from django's default authentication application.

    It removes the username field and replaces it instead by
    the email address. In order to handle the modifications,
    it uses a custom UserManager.
    """

    # Remove username field
    username = None

    # Substitute username by email address field
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'

    # Use custom UserManager for user creation
    REQUIRED_FIELDS = []
    objects = managers.UserManager()


class LoginToken(models.Model):
    """Login token model.

    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    token = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class EmailAddress(models.Model):
    """Email address model.

    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    email = models.EmailField(unique=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    def verify(self, token):
        if self.verification_token == token:
            self.verification_token = None
            self.verified_at = datetime.now()
            self.save()
            return self
        raise ValidationError('Wrong token.')

    def make_primary(self):
        for email in self.objects.filter(user=self.user):
            if email == self:
                if not self.is_primary:
                    self.is_primary = True
                    self.save()
            else:
                if email.is_primary:
                    email.is_primary = False
                    email.save()

    def send_verification(self):
        verification_token = EmailVerificationToken.create(self)
        verification_token.sent_at = datetime.now()
        verification_token.save()
        send_mail(
            'Email address confirmation',
            verification_token.token,
            'avs@zs.dev',
            self.email
        )


class EmailVerificationToken(models.Model):
    """Email verification token model.

    """

    email_address = models.ForeignKey(
        EmailAddress,
        on_delete=models.CASCADE
    )
    token = models.CharField(max_length=32)
    sent_at = models.DateTimeField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    object = managers.EmailVerificationTokenManager()

    def __str__(self):
        return self.token

    @classmethod
    def create(cls, email_address):
        token = get_random_string(32)
        return cls(email_address=email_address, token=token)

    def is_expired(self):
        pass

    def send(self):
        pass