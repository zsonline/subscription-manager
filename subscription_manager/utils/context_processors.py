# Django imports
from django.conf import settings

# Project imports
from subscription_manager.utils.language import humanize_list

def setting_variables(request):
    return {
        'allowed_student_email_addresses': humanize_list(['@' + s for s in settings.ALLOWED_STUDENT_EMAIL_ADDRESSES], 'und'),
}