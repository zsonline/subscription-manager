# Django imports
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone


class SubscriptionManager(models.Manager):
    """
    Custom manager for payments.
    """
    def expire_today(self):
        subscriptions = self.filter(end_date=timezone.now().date()).filter(canceled_at__isnull=True)

    @staticmethod
    def send_expiration_email(subscription):
        """
        Sends expiration email for a given
        subscription.
        """
        # Make a context variable for the templates
        context = {
            'to_name': subscription.user.first_name,
            'from_name': settings.ORGANISATION_NAME,
        }
        # Render the content templates
        text_content = render_to_string('subscription/emails/expiration.txt', context)
        html_content = render_to_string('subscription/emails/expiration.html', context)
        # Create the text and html version of the email
        message = EmailMultiAlternatives(
            subject='Abo abgelaufen',
            body=text_content,
            from_email=settings.ORGANISATION_FROM_EMAIL,
            to=[subscription.user.email],
            headers={
                'Reply-To': settings.ORGANISATION_REPLY_TO_EMAIL
            }
        )
        message.attach_alternative(html_content, 'text/html')
        # Send the email
        message.send()