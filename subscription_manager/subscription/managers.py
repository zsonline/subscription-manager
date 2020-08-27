import calendar
import datetime

from django.apps import apps
from django.conf import settings
from django.core.mail import send_mass_mail
from django.db import models
from django.db.models import BooleanField, Case, DateField, IntegerField, Q, Max, Min, Sum, When
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

    def get_active_by_month(self, year, month):
        """
        Returns all subscriptions that were active in the given month.
        """
        start_date = datetime.datetime(year, month, 1).date()

        end_day = calendar.monthrange(year, month)[1]
        end_date = datetime.datetime(year, month, end_day).date()

        return self.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        )

    def get_new_by_month(self, year, month):
        """
        Returns all subscriptions that were newly created in the given month.
        """
        return self.filter(
            start_date__year=year,
            start_date__month=month
        )

    def get_renewed_by_month(self, year, month):
        """
        Returns all subscriptions that were renewed in the given month.
        """
        return self.annotate(
            active_periods_in_month_sum=Sum(
                Case(
                    When(
                        Q(
                            period__start_date__isnull=False,
                            period__end_date__isnull=False,
                            period__start_date__year=year,
                            period__start_date__month=month,
                            period__payment__paid_at__isnull=False
                        ) |
                        Q(
                            period__start_date__isnull=False,
                            period__end_date__isnull=False,
                            period__end_date__year=year,
                            period__end_date__month=month,
                            period__payment__paid_at__isnull=False
                        ),
                        then=1
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            ),
        ).filter(
            active_periods_in_month_sum=2
        )

    def get_expired_by_month(self, year, month):
        """
        Returns all subscriptions that expired in the given month.
        """
        return self.filter(
            canceled_at__isnull=True,
            end_date__year=year,
            end_date__month=month
        )

    def get_canceled_by_month(self, year, month):
        """
        Returns all subscriptions that were canceled in the given month.
        """
        return self.filter(
            canceled_at__year=year,
            canceled_at__month=month
        )

    def get_expiring(self, timedelta=timezone.timedelta(days=30)):
        """
        Returns all subscriptions that expire.
        """
        # Get all expiring subscriptions
        end_date = (timezone.now() + timedelta).date()
        expiring_subscriptions = self.filter(is_canceled=False, end_date=end_date)
        return expiring_subscriptions


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
