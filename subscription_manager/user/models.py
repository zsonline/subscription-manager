import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMessage
from django.db import models, transaction, IntegrityError
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
        return '{} ({})'.format(self.full_name(), self.email)

    def email_domain(self):
        """
        Returns the user's email domain.
        """
        return self.email.split('@')[-1]

    def verified_email_domains(self):
        """
        Returns a list of all verified email domain.
        """
        email_addresses = self.emailaddress_set.filter(verified_at__isnull=False)

        # Exclude email addresses which have not been verified in the last 30 days.
        exclude_pks = []
        for email_address in email_addresses:
            if not email_address.recently_verified(timezone.timedelta(days=30)):
                exclude_pks.append(email_address.pk)
        email_addresses = email_addresses.exclude(pk__in=exclude_pks)

        email_addresses = map(lambda email: email['email'].split('@')[-1], email_addresses.values('email'))
        return list(email_addresses)

    def full_name(self):
        """
        Returns the user's full name.
        """
        return '{} {}'.format(self.first_name, self.last_name)

    def primary_email(self):
        """
        Return the primary email address object.
        """
        return EmailAddress.objects.get(user=self, is_primary=True)

    def save(self, *args, **kwargs):
        # If it is a new object, create an email address object
        is_created = self.id is None
        if is_created:
            try:
                super().save(*args, **kwargs)
                EmailAddress.objects.create(user=self, email=self.email, is_primary=True)
            except IntegrityError:
                pass
        else:
            super().save(*args, **kwargs)


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
    is_verified.boolean = True

    def recently_verified(self, timedelta=timezone.timedelta(days=30)):
        """
        Returns true if the email address has already been
        verified in given timedelta. Default: one day.
        """
        if self.verified_at is None:
            return False
        return self.verified_at.date() > timezone.now().date() - timedelta
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
            raise self.EmailAddressIsPrimaryException

        # Delete email address
        super().delete(using, keep_parents)

    def verify(self):
        """
        Sets the verified at attribute to the current datetime.
        """
        self.verified_at = timezone.now()
        self.save()

    class EmailAddressIsPrimaryException(Exception):
        pass


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
            ('verification', 'E-Mail-Adresse verifizieren'),
            ('login', 'Login'),
            ('signup', 'Registrierung abschliessen')
        ),
        verbose_name='Zweck'
    )
    code = models.UUIDField(
        unique=True,
        editable=False,
        verbose_name='Code'
    )
    valid_until = models.DateTimeField(
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
        return str(self.code)

    def is_valid(self):
        """
        True if the token is valid.
        """
        return timezone.now() <= self.valid_until
    is_valid.boolean = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Overrides the default save method. It checks whether a token can be created
        by a user and generates a uuid code.
        """
        # If object is newly created
        if not self.pk:
            # Limit token creation
            user = self.email_address.user
            if user is None:
                raise ValueError
            if Token.objects.count_created_in_last_hour(user) >= settings.TOKENS_PER_USER_PER_HOUR:
                raise self.TokenQuotaExceededError

            # Set valid until
            self.valid_until = timezone.now() + settings.TOKEN_EXPIRATION

            # Try creating a token object
            while True:
                try:
                    # Generates a UUID
                    code = uuid.uuid4()
                    self.code = code
                    # Try creating token object
                    super().save(force_insert, force_update, using, update_fields)
                except IntegrityError:
                    continue
                break

        # If object existed already
        else:
            super().save(force_insert, force_update, using, update_fields)

    def url(self):
        """
        Returns the url for a given code.
        Example: https://www.hostname.tld/auth/token/1836af19-67df-4090-8229-16ed13036480/
        """
        return '{}{}'.format(
            settings.BASE_URL,
            reverse(
                'token_verification',
                kwargs={
                    'code': self.code
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
        url = self.url()
        if next_page is not None:
            url += '?next=' + next_page

        # Send email
        email = EmailMessage(
            subject=settings.EMAIL_SUBJECT_PREFIX + subject,
            body=render_to_string(template, {
                'to_name': self.email_address.user.first_name,
                'token': self
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            reply_to=[settings.DEFAULT_REPLY_TO_EMAIL],
            to=[self.email_address.email]
        )
        email.send(fail_silently=False)

        # Update sent_at field
        self.sent_at = timezone.now()
        self.save()

    class TokenQuotaExceededError(Exception):
        """
        Raised when the token quota has been exceeded by a user.
        """
        pass

