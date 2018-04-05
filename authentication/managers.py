# Python imports
import hashlib
import uuid

# Django imports
from django.db import models, IntegrityError
from django.conf import settings
from django.utils import timezone


class LoginTokenManager(models.Manager):
    """
    Custom manager for login tokens.
    """

    def create(self, code, **obj_data):
        """
        Overrides the default create method. It sets the valid_until
        attribute and generates a random code.
        """
        # Set token expiration
        obj_data['valid_until'] = timezone.now() + settings.TOKEN_EXPIRATION

        # Set code and create LoginToken object
        encoded_code = hashlib.sha256(str(code).encode('utf-8')).hexdigest()
        obj_data['code'] = encoded_code

        # Try creating the object
        token = super().create(**obj_data)
        return token

    def create_and_send(self, **obj_data):
        """
        Creates and sends a token object.
        """
        code = uuid.uuid4()
        token = self.create(code, **obj_data)
        token.send(code)
        return token

    def all_expired(self):
        """Selects all tokens that have been sent more than seven days ago"""
        return self.filter(
            sent_at__lt=timezone.now() - settings.TOKEN_EXPIRATION
        )

    def delete_all_expired(self):
        self.all_expired().delete()
