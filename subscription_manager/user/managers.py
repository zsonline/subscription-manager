from django.contrib.auth.models import BaseUserManager


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

        # Set password if one was provided. Otherwise, set
        # an unusable one
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