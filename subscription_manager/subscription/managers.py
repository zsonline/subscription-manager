from django.apps import apps
from django.conf import settings
from django.core.mail import send_mass_mail
from django.db import models
from django.db.models import BooleanField, Case, DateField, IntegerField, Max, Min, Sum, When
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

            # Exclude plans for which the user's email domain is not eligible
            verified_email_domains = user.verified_email_domains()
            for plan in plans:
                eligible_email_domains = plan.get_eligible_email_domains()
                if eligible_email_domains and not any(email in verified_email_domains for email in eligible_email_domains):
                    plans = plans.exclude(id=plan.id)

        return plans


class SubscriptionManager(models.Manager):

    def get_queryset(self):
        """
        Annotate queryset with computed fields is_canceled, active_periods_sum,
        is_active, unpaid_payments_sum, is_paid, start_date, and end_date.
        """
        queryset = super().get_queryset()
        # Annotate queryset with columns is_canceled, active_periods_sum,
        # is_active, unpaid_payments_sum, is_paid, start_date, and end_date.
        queryset = queryset.annotate(
            is_canceled=Case(
                When(
                    canceled_at__isnull=False,
                    then=True
                ),
                default=False,
                output_field=BooleanField()
            ),
            active_periods_sum=Sum(
                Case(
                    When(
                        canceled_at__isnull=True,
                        period__start_date__isnull=False,
                        period__end_date__isnull=False,
                        period__start_date__lte=timezone.now().date(),
                        period__end_date__gt=timezone.now().date(),
                        period__payment__paid_at__isnull=False,
                        then=1
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            is_active=Case(
                When(
                    active_periods_sum__gte=1,
                    then=True
                ),
                default=False,
                output_field=BooleanField()
            ),
            unpaid_payments_sum=Sum(
                Case(
                    When(
                        period__payment__paid_at__isnull=True,
                        then=1
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            is_paid=Case(
                When(
                    unpaid_payments_sum=0,
                    then=True
                ),
                default=False,
                output_field=BooleanField()
            ),
            start_date=Min(
                Case(
                    When(
                        period__payment__paid_at__isnull=False,
                        then='period__start_date'
                    ),
                    default=None,
                    output_field=DateField()
                )
            ),
            end_date=Max(
                Case(
                    When(
                        period__payment__paid_at__isnull=False,
                        then='period__end_date'
                    ),
                    default=None,
                    output_field=DateField()
                )
            )
        )
        return queryset

    def get_expiring(self, timedelta=timezone.timedelta(days=30)):
        """
        Returns all subscriptions that expire.
        """
        # Get all expiring subscriptions
        end_date = (timezone.now() + timedelta).date()
        expiring_subscriptions = self.filter(is_canceled=False, end_date=end_date)
        return expiring_subscriptions

    def send_expiration_emails(self, queryset=None, remaining_days=None):
        """
        Sends an email to users whose subscriptions expire.
        """
        if remaining_days is None and queryset is None:
            return
        # Get all expiring subscriptions which are renewable
        if queryset is None:
            queryset = self.get_expiring(timezone.timedelta(days=remaining_days)).filter(plan__is_renewable=True)

        # Loop through subscriptions and send an reminder email to all users
        token_model = apps.get_model('user', 'Token')
        messages = []
        for subscription in queryset:
            # If subscription is not owned by a user, skip
            user = subscription.user
            if user is None:
                continue

            # Create login token
            token = token_model.objects.create(email_address=user.primary_email(), purpose='login')

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
