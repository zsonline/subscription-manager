import uuid

from django.db import models, IntegrityError
from django.utils import timezone


class TokenManager(models.Manager):
    """
    Custom manager for tokens.
    """
    def create(self, **obj_data):
        """
        Overrides the default create method. It sets the valid_until
        attribute and generates a random code.
        """
        # Try creating LoginToken object
        while True:
            try:
                # Generates a UUID
                code = uuid.uuid4()
                # Try creating token object
                obj_data['code'] = code
                token = super().create(**obj_data)
            except IntegrityError:
                continue
            break
        return token

    def create_and_send(self, next_page=None, **obj_data):
        """
        Creates and sends a token object.
        """
        # Create and send token
        token = self.create(**obj_data)
        token.send(next_page)
        return token

    def filter_valid(self, user, action):
        return self.filter(
            user=user,
            action=action,
            valid_until__gte=timezone.now()
        )

    def all_expired(self):
        """
        Selects all expired tokens.
        """
        return self.filter(
            valid_until__lt=timezone.now()
        )

