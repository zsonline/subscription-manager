# Django imports
from django.contrib.auth.models import BaseUserManager
from django.db import models, IntegrityError
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class LoginTokenManager(models.Manager):
    """
    Custom manager for login tokens.
    """

    def create(self, **obj_data):
        """
        Overrides the default create method. It sets the valid_until
        attribute and generates a random code.
        """
        # Set token expiration
        obj_data['valid_until'] = timezone.now() + settings.TOKEN_EXPIRATION

        # Set code and create LoginToken object
        while True:
            # Generate a random token
            obj_data['code'] = get_random_string(settings.TOKEN_LENGTH)
            # Try creating the object
            try:
                token = super().create(**obj_data)
            # If token already exists, generate a new one and try again
            except IntegrityError:
                continue
            # Token successfully created, return
            break

        return token

    def create_and_send(self, **obj_data):
        """
        Creates and sends a token object.
        """
        token = self.create(**obj_data)
        token.send()
        return token

    def all_expired(self):
        """Selects all tokens that have been sent more than seven days ago"""
        return self.filter(
            sent_at__lt=timezone.now() - settings.TOKEN_EXPIRATION
        )

    def delete_all_expired(self):
        self.all_expired().delete()
