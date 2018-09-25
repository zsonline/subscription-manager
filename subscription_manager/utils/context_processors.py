# Django imports
from django.conf import settings


def setting_variables(request):
    return {
        'organisation_name': settings.ORGANISATION_NAME,
        'organisation_abbreviation': settings.ORGANISATION_ABBREVIATION,
        'allowed_student_email_addresses': settings.ALLOWED_STUDENT_EMAIL_ADDRESSES,
        'announcement': settings.ANNOUNCEMENT,
        'announcement_class': settings.ANNOUNCEMENT_CLASS
}