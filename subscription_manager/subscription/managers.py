# Django imports
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone


class SubscriptionManager(models.Manager):
    """
    Custom manager for payments.
    """
    def notify_to_be_expired_subscribers(self):
        """
        Sends an email to users whose subscriptions
        expire.
        """
        subscriptions = self.all_expire_in(30)
        for subscription in subscriptions:
            self.send_expiration_email(subscription)

    def all_expire_in(self, days):
        """
        Returns all subscriptions that expire in a
        given amount of days (exactly).
        """
        subscriptions = self.filter(end_date=timezone.now().date()+timezone.timedelta(days=days)).filter(canceled_at__isnull=True)
        return subscriptions

    def has_student_subscriptions(self, user):
        """
        Returns true if given user has no student
        subscription.
        """
        # Get all subscriptions of a user
        subscriptions = self.filter(user=user)
        # Exclude inactive or non-student subscriptions
        to_be_removed = []
        for subscription in subscriptions:
            if not (subscription.plan.slug == 'student' and subscription.is_active()):
                to_be_removed.append(subscription.id)
        subscriptions.exclude(id__in=to_be_removed)
        # Return true if count is 0
        return subscriptions.count() > 0

    @staticmethod
    def send_expiration_email(subscription):
        """
        Sends expiration email for a given
        subscription.
        """
        send_mail(
            subject=settings.EMAIL_SUBJECT_PREFIX + 'Abo verlängern',
            message=render_to_string('emails/expiration.txt', {
                'to_name': subscription.user.first_name,
                'subscription': subscription,
                'url': '{}{}'.format(settings.BASE_URL, reverse('login'))
                       + '?next=' + reverse('payment_create', kwargs={'subscription_id': subscription.id})
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscription.user.email],
            fail_silently=False
        )
