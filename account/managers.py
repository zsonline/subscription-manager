from datetime import datetime, timedelta

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
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


class EmailVerificationTokenManager(models.Manager):

    def all_expired(self):
        """Selects all tokens that have been sent more than seven days ago"""
        return self.filter(
            sent_at__lt=datetime.now() - timedelta(days=settings.EMAIL_VERIFICATION_TOKEN_EXPIRATION_DAYS)
        )

    def delete_all_expired(self):
        self.all_expired().delete()
