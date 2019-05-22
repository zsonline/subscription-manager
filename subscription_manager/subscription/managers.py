from django.apps import apps
from django.conf import settings
from django.core.mail import send_mass_mail
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
            verified_email_domains = user.verified_email_domains()
            for plan in plans:
                eligible_email_domains = plan.get_eligible_email_domains()
                if eligible_email_domains and not any(email in verified_email_domains for email in eligible_email_domains):
                    plans = plans.exclude(id=plan.id)

        return plans


class SubscriptionManager(models.Manager):

    def get_expiring(self, timedelta=timezone.timedelta(days=30)):
        """
        Returns all subscriptions that expire.
        """
        # Get all expiring periods
        period_model = apps.get_model('period', 'Period')
        expiring_periods = period_model.objects.get_active().filter(end_date=timezone.now().date+timedelta)
        # Get subscription of these periods, which have not been canceled
        subscriptions = self.filter(canceled_at__isnull=True).filter(period__in=expiring_periods)
        return subscriptions

    def send_expiration_emails(self):
        """
        Sends an email to users whose subscriptions expire.
        """
        # Get all expiring subscriptions
        expiring_subscriptions = self.get_expiring(timezone.timedelta(days=30))

        # Loop through subscriptions and send an reminder email to all users
        token_model = apps.get_model('token', 'Token')
        messages = []
        for subscription in expiring_subscriptions:
            # If subscription is not owned by a user, skip
            user = subscription.user
            if user is None:
                continue
            # Create login token
            token = token_model.objects.create(email_address=user.primary_email(), purpose='login')
            # Add expiration email message
            messages.append((
                settings.EMAIL_SUBJECT_PREFIX + 'Abo verlängern',
                render_to_string('emails/subscription_expiration.txt', {
                    'to_name': user.first_name,
                    'subscription_id': subscription.id,
                    'token': token
                }),
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            ))

        # Send all expiration emails
        send_mass_mail(tuple(messages), fail_silently=False)


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
