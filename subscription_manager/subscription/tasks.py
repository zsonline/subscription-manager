from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone

from subscription_manager.user.models import Token

from .models import Subscription


def send_expiration_emails(queryset=None, remaining_days=None):
    """
    Sends an email to users whose subscriptions expire.
    """
    if remaining_days is None and queryset is None:
        return
    # Get all expiring subscriptions which are renewable
    if queryset is None:
        queryset = Subscription.objects.get_expiring(timezone.timedelta(days=remaining_days)).filter(plan__is_renewable=True)

    # Loop through subscriptions and send an reminder email to all users
    messages = []
    for subscription in queryset:
        # If subscription is not owned by a user, skip
        user = subscription.user
        if user is None:
            continue

        # Create login token
        token = Token.objects.create(email_address=user.primary_email(), purpose='login')

        # Add expiration email message
        if remaining_days is None:
            subject = settings.EMAIL_SUBJECT_PREFIX + 'Abo verlängern'
            remaining_days_text = 'bald'
        elif remaining_days == 1:
            subject = settings.EMAIL_SUBJECT_PREFIX + 'Abo endet heute'
            remaining_days_text = 'heute'
        else:
            subject = settings.EMAIL_SUBJECT_PREFIX + 'Abo verlängern'
            remaining_days_text = 'in {} Tagen'.format(remaining_days)

        messages.append((
            subject,
            render_to_string('emails/subscription_expiration.txt', {
                'to_name': user.first_name,
                'subscription_id': subscription.id,
                'token': token,
                'remaining_days': remaining_days_text
            }),
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        ))

    # Send all expiration emails
    send_mass_mail(tuple(messages), fail_silently=False)
