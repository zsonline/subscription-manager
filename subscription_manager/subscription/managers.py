from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone


class PlanManager(models.Manager):

    def filter_eligible(self, user=None, purpose='purchase'):
        """
        Returns plans for which a user is eligible.
        """
        if purpose == 'purchase':
            # Filter purchasable plans
            plans = self.filter(
                is_purchasable=True
            ).exclude(
                eligible_active_subscriptions_per_user=0
            )
        elif purpose == 'renewal':
            # Filter renewable plans
            plans = self.filter(
                is_renewable=True
            ).exclude(
                eligible_active_subscriptions_per_user=0
            )
        else:
            return None

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
                        num_subs_of_plan__lt=models.F('plan__eligible_active_subscriptions_per_user')
                    )
            )

            # Exclude plans for which the user's email domain is not eligible
            verified_email_domains = user.verified_email_domains
            for plan in plans:
                eligible_email_domains = plan.get_eligible_email_domains()
                if eligible_email_domains and not any(email in verified_email_domains for email in eligible_email_domains):
                    plans = plans.exclude(id=plan.id)

        return plans


class SubscriptionManager(models.Manager):

    # TODO:

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


class PeriodManager(models.Manager):

    def get_active(self, subscription=None):
        """
        Filters active periods. If a subscription is given it also
        filters by that subscription.
        """
        # Select periods which are related to subscription if given
        if subscription is not None:
            periods = self.filter(subscription=subscription)
        else:
            periods = self.all()

        # Filter active periods
        periods = periods.filter(start_date__isnull=False, start_date__lte=timezone.now().date(),
                       end_date__isnull=False, end_date__gt=timezone.now().date(),
                       payment__paid_at__isnull=False)

        return periods
