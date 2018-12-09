from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone


class PlanManager(models.Manager):

    def filter_eligible(self, user=None):
        """
        Returns plans for which a user is eligible.
        """
        # Filter active plans
        plans = self.filter(
            is_active=True,
        ).exclude(
            max_active_subscriptions_per_user=0,
        )

        # If user is logged in, perform additional checks
        if user is not None and user.is_authenticated:

            # Exclude plans for which the user has reached the maximum allowed amount
            subscription_model = apps.get_model('subscription', 'Subscription')
            now = timezone.now().date()
            plans = plans.exclude(
                subscription__in=subscription_model.objects.filter(
                        user=user,
                        period__end_date__gt=now,
                        period__start_date__lte=now,
                        canceled_at__isnull=True
                    ).annotate(
                        num_subs_of_plan=models.Count('plan__id')
                    ).exclude(
                        num_subs_of_plan__lt=models.F('plan__max_active_subscriptions_per_user')
                    )
            )

            # Exclude plans for which the user's email domain is not eligible
            email_domain = user.get_email_domain()
            for plan in plans:
                eligible_email_domains = plan.get_eligible_email_domains()
                if eligible_email_domains and email_domain not in eligible_email_domains:
                    plans = plans.exclude(id=plan.id)

        return plans


class SubscriptionManager(models.Manager):
    #TODO:--------------

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
        count = 0
        for subscription in subscriptions:
            if subscription.plan.slug == 'student' and subscription.is_active():
                count += 1
        # Return true if count is 0
        return count > 0

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
