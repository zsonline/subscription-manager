import uuid

from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.db import models, IntegrityError
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Private method, which is called by create_user
        and create_superuser. Creates and saves the user
        to the database.
        """
        # Verify that email is set
        if not email:
            raise ValueError('The given email must be set')

        # Clean email
        email = self.normalize_email(email)
        # Create user object
        user = self.model(email=email, **extra_fields)

        # Set password if one was provided. Otherwise, set an unusable one
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Manager for handling regular user creation.
        """
        # Sets default values
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Manager for handling superuser creation.
        """
        # Sets default values if not provided
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Verify values
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class TokenManager(models.Manager):
    """
    Custom manager for tokens.
    """
    def create(self, **obj_data):
        """
        Catch exceptions and return null instead of rasing an exception.
        """
        try:
            token = super().create(**obj_data)
        except self.model.TokenQuotaExceededError:
            token = None

        return token

    def create_and_send(self, next_page=None, **obj_data):
        """
        Creates and sends a token object.
        """
        # Create and send token
        token = self.create(**obj_data)
        if token is not None:
            token.send(next_page)
        return token is not None

    def filter_valid(self, user, purpose=None):
        """
        Returns all valid tokens for a given user. Furthermore,
        it can be filtered by purpose.
        """
        email_addresses = user.emailaddress_set.all()
        if purpose is None:
            # Filter all tokens independent from their purpose
            return self.filter(
                email_address__in=email_addresses,
                valid_until__gte=timezone.now()
            )
        # Filter purpose
        return self.filter(
            email_address__in=email_addresses,
            purpose=purpose,
            valid_until__gte=timezone.now()
        )

    def count_created_in_last_hour(self, user, purpose=None):
        """
        Returns the count of tokens which were created in the
        last hour. The amount of hours can be specified as a
        parameter. The count can also be filtered by purpose.
        """
        email_addresses = user.emailaddress_set.all()
        if purpose is None:
            # Count tokens that are independent from their purpose
            return self.filter(
                email_address__in=email_addresses,
                created_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
        # Count filter with purpose
        return self.filter(
            email_address__in=email_addresses,
            purpose=purpose,
            created_at__gte=timezone.now() - timezone.timedelta(hours=1)
        ).count()

    def all_expired(self):
        """
        Selects all expired tokens.
        """
        return self.filter(
            valid_until__lt=timezone.now()
        )
