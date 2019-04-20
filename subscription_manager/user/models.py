from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models, transaction
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone

from .managers import UserManager, TokenManager


class User(AbstractUser):
    """
    Custom user model that inherits the AbstractUser model
    from django's default authentication application. It
    removes the username field and replaces it instead by
    the email address.
    """
    # Remove username field
    username = None
    first_name = models.CharField(
        max_length=30,
        verbose_name='Vorname'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Nachname'
    )
    # Make email address unique
    email = models.EmailField(
        unique=True,
        verbose_name='E-Mail-Adresse'
    )

    # Substitute username by email address field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return '{} ({})'.format(self.full_name, self.email)

    def _get_email_domain(self):
        """
        Returns the user's email domain.
        """
        return self.email.split('@')[-1]
    email_domain = property(_get_email_domain)

    def _get_verified_email_domains(self):
        """
        Returns a list of all verified email domain.
        """
        email_addresses = self.emailaddress_set.filter(verified_at__isnull=False).values('email')
        email_addresses = map(lambda email: email['email'].split('@')[-1], email_addresses)
        return list(email_addresses)
    verified_email_domains = property(_get_verified_email_domains)

    def _get_full_name(self):
        """
        Returns the user's full name.
        """
        return '{} {}'.format(self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def _get_primary_email(self):
        """
        Return the primary email address object.
        """
        return EmailAddress.objects.get(user=self, is_primary=True)
    primary_email = property(_get_primary_email)

    def save(self, *args, **kwargs):
        is_created = self.id is None

        super().save(*args, **kwargs)

        # If it is a new object, create an email address object
        if is_created:
            EmailAddress.objects.create(user=self, email=self.email, is_primary=True)

        return super().save(*args, **kwargs)


class EmailAddress(models.Model):
    """
    A user can have multiple email addresses. Those can
    be verified and used to order subscriptions which are
    restricted for certain email address domains. The primary
    email address is used for authentication and also stored
    in the user model as email/username.
    """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Account'
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name='E-Mail-Adresse',
        error_messages={
            'unique': 'Diese E-Mail-Adresse existiert bereits.'
        }
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='ist primär'
    )
    verified_at = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name='verifiziert am'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='erstellt am'
    )

    class Meta:
        verbose_name = 'E-Mail-Adresse'
        verbose_name_plural = 'E-Mail-Adressen'

    def __str__(self):
        return self.email

    def is_verified(self):
        """
        Returns true if a verified at attribute is set.
        """
        return self.verified_at is not None

    def recently_verified(self, timedelta=timezone.timedelta(days=1)):
        """
        Returns true if the email address has already been
        verified in given timedelta. Default: one day.
        """
        if self.verified_at is None:
            return False
        return self.verified_at.date() > timezone.now() - timedelta
    recently_verified.boolean = True

    @transaction.atomic
    def set_primary(self):
        """
        Make this email address the primary address by setting
        it as the user's email address, its is_primary value to true
        and all other email addresses' is_primary value to false.
        """
        self.user.email = self.email
        self.user.save()
        for email in self.user.emailaddress_set.all():
            if email == self:
                if not email.is_primary:
                    email.is_primary = True
                    email.save()
            else:
                if email.is_primary:
                    email.is_primary = False
                    email.save()

    def delete(self, using=None, keep_parents=False):
        """
        Delete only if the email address is not set as primary.
        """
        # Check that it the email address is not primary
        if self.is_primary:
            raise Exception

        # Delete email address
        super().delete(using, keep_parents)

    def send_verification(self):
        """
        Creates a token for verification and sends it
        to this email address. Returns true if it was successful.
        """
        token = Token.objects.create_and_send(email_address=self, purpose='verification')
        return token is not None

    def verify(self):
        """
        Sets the verified at attribute to the current datetime.
        """
        self.verified_at = timezone.now()
        self.save()


class Token(models.Model):
    """
    Tokens are used for login or email verification. It is
    associated with an email address and can be sent to it.
    """
    email_address = models.ForeignKey(
        to=EmailAddress,
        on_delete=models.CASCADE,
        verbose_name='E-Mail-Adresse'
    )
    purpose = models.CharField(
        max_length=20,
        choices=(
            ('verification', 'Bestätigung'),
            ('login', 'Login')
        ),
        verbose_name='Zweck'
    )
    code = models.UUIDField(
        unique=True,
        editable=False,
        verbose_name='Code'
    )
    valid_until = models.DateTimeField(
        default=timezone.now() + settings.TOKEN_EXPIRATION,
        verbose_name='gültig bis'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='gesendet am'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='erstellt am'
    )

    objects = TokenManager()

    class Meta:
        verbose_name = 'Token'

    def __str__(self):
        return self.code

    def is_valid(self):
        """
        True if the token is valid.
        """
        return timezone.now() <= self.valid_until

    @staticmethod
    def url(code):
        """
        Returns the url for a given code.
        Example: https://www.hostname.tld/auth/token/1836af19-67df-4090-8229-16ed13036480/
        """
        return '{}{}'.format(
            settings.BASE_URL,
            reverse(
                'token_verification',
                kwargs={
                    'code': code
                }
            )
        )

    def send(self, next_page=None):
        """
        Sends an email with the token code and updates the
        sent_at field.
        """
        # Select template
        template = 'emails/token_' + self.purpose + '.txt'
        subject = self.get_purpose_display()

        # Generate url
        url = Token.url(self.code)
        if next_page is not None:
            url += '?next=' + next_page

        # Send email
        send_mail(
            subject=settings.EMAIL_SUBJECT_PREFIX + subject,
            message=render_to_string(template, {
                'to_name': self.email_address.user.first_name,
                'url': url,
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email_address.email],
            fail_silently=False
        )

        # Update sent_at field
        self.sent_at = timezone.now()
        self.save()
