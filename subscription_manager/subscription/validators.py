from django.core.exceptions import ValidationError


class RequiredKeysValidator:
    """
    Checks if a dictionary object contains the
    required keys.
    """

    def __init__(self, keys):
        """
        Initialises the validator.
        """
        self.required_keys = keys

    def __call__(self, value):
        """
        Performs validation of a given value.
        """
        for key in self.required_keys:
            if key not in value:
                raise ValidationError(
                    '{} must be specified.'.format(key)
                )
