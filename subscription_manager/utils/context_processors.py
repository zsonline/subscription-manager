# Django imports
from django.conf import settings


def setting_variables(request):
    return {
        'organisation_name': settings.ORGANISATION_NAME,
        'organisation_abbreviation': settings.ORGANISATION_ABBREVIATION
}