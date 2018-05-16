# Django imports
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def organisation(request):
    return {
        'organisation_name': settings.ORGANISATION_NAME,
        'organisation_abbreviation': settings.ORGANISATION_ABBREVIATION
    }
