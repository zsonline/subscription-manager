from datetime import date

from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from .managers import PlanManager, SubscriptionManager


class Plan(models.Model):
    """
    Model that holds the data for a plan (a type of subscription). Such a plan
    can or cannot be purchased by users.
    """
    # Model fields
    name = models.CharField(
        'Name',
        max_length=50
    )
    description = models.TextField(
        'Beschreibung',
        null=True,
        blank=True
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )
    duration_in_months = models.PositiveIntegerField(
        'Laufzeit in Monaten',
        default=12,
        help_text='Die Laufzeit muss in Monaten angegeben sein.'
    )  # In months
    price = models.PositiveIntegerField('Preis')
    is_active = models.BooleanField(
        'Ist aktiv',
        default=True,
        help_text='Dieser Wert bestimmt, ob das Abo gekauft oder verlängert werden kann.'
    )
    eligible_email_domains = models.TextField(
        'Berechtigte E-Mail-Domains',
        null=True,
        blank=True,
        help_text='E-Mail-Adressen müssen mit einem Semikolon getrennt sein.'
    )
    max_active_subscriptions_per_user = models.PositiveIntegerField(
        'Anzahl aktiver Abos pro Leserin',
        null=True,
        blank=True,
        help_text='Kein Wert bedeutet, dass es keine Begrenzung gibt.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Abotyp'
        verbose_name_plural = 'Abotypen'

    # Custom manager
    objects = PlanManager()

    def __str__(self):
        return self.name

    def get_eligible_email_domains(self):
        """
        Returns a list of the eligible email domains.
        """
        if self.eligible_email_domains is None:
            return []

        eligible_email_domains_list = self.eligible_email_domains.split(';')
        return list(filter(None, eligible_email_domains_list))

    def get_readable_eligible_email_domains(self, conjunction='und'):
        """
        Returns a readable string of the eligible email domains.
        """
        # Prefixes the @-symbol to all domains
        eligible_email_domains = ['@' + email_domain for email_domain in self.get_eligible_email_domains()]

        # Convert list to string of comma- and conjunction-separated domains and return
        if len(eligible_email_domains) == 0:
            return ''
        elif len(eligible_email_domains) == 1:
            return eligible_email_domains[0]
        else:
            return ', '.join(eligible_email_domains[:-1]) + ' ' + conjunction + ' ' + eligible_email_domains[-1]


class Subscription(models.Model):
    """
    Model that holds the data for a user's subscription (an instance of a plan).
    A purchased plan corresponds to a subscription.
    """
    # Model fields
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    plan = models.ForeignKey(
        'Plan',
        on_delete=models.PROTECT,
        verbose_name='Abotyp'
    )
    address_line_1 = models.CharField(
        'Adresse',
        max_length=50
    )
    address_line_2 = models.CharField(
        'Adresszusatz',
        max_length=50,
        blank=True,
        null=True,
    )
    postcode = models.CharField(
        'Postleitzahl',
        max_length=8,
    )
    city = models.CharField(
        'Ort',
        max_length=50
    )
    country = models.CharField(
        'Land',
        max_length=50,
        default='Schweiz'
    )
    canceled_at = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Custom manager
    objects = SubscriptionManager()

    class Meta:
        verbose_name = 'Abo'
        verbose_name_plural = 'Abos'

    def __str__(self):
        return '{} #{} von {}'.format(self.plan, self.id, self.user.full_name())

    def is_canceled(self):
        """
        Returns true if the canceled_at field is set.
        """
        return self.canceled_at is not None
    is_canceled.boolean = True

    def is_active(self):
        """
        Returns true if the subscription has not been canceled and one active period exists.
        """
        return not self.is_canceled() and self.objects.filter_active_periods().count() == 1
    is_active.boolean = True

    def renew(self):
        """
        Renews the subscription by the duration of the plan.
        """
        #TODO:
        self.end_date += relativedelta(months=self.plan.duration)
        self.save()
        return self

    def has_open_payments(self):
        """
        Returns true if at least one payment associated with
        this subscription is open. Otherwise false.
        """#TODO:
        payments = self.payment_set.all()
        if payments is None:
            return False
        for payment in payments:
            if not payment.is_paid():
                return True
        return False

    def last_payment_amount(self):
        """
        Returns the last payment's amount. If no
        payment exists, None is returned.
        """#TODO:
        try:
            last_payment = self.payment_set.latest('created_at')
        except ObjectDoesNotExist:
            return None
        return last_payment.amount

    def expires_in_lt(self, days):
        """
        Returns true if subscription expires in less than
        the given amount of days.
        """#TODO:
        # Check if end_date is instance of date
        if self.end_date >= timezone.now().date():
            return self.end_date - timezone.now().date() <= timezone.timedelta(days=days)
        return False

    def expires_soon(self):
        """#TODO:
        Returns true if subscription expires in less than
        30 days.
        """
        return self.expires_in_lt(30)


class Period(models.Model):
    """
    Model that holds data of a period. A period is one cycle of a user's
    subscription. If a user renews her subscription, a new period is created
    for that subscription.
    """
    # Model fields
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='Abonnement'
    )
    start_date = models.DateField(
        null=True,
        blank=True
    )
    end_date = models.DateField(
        null=True,
        blank=True
    )
    amount = models.PositiveIntegerField('Betrag')
    paid_at = models.DateTimeField(
        'Bezahlt am',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Periode'
        verbose_name_plural = 'Perioden'

    def __str__(self):
        return 'Periode vom {} bis {} für {}'.format(self.start_date, self.end_date, self.subscription)

    def has_started(self):
        """
        True if the period has started.
        """
        return self.start_date is not None and self.start_date <= timezone.now().date()
    has_started.boolean = True

    def has_ended(self):
        """
        True if the period has ended.
        """
        return self.end_date is not None and self.end_date <= timezone.now().date()
    has_ended.boolean = True

    def is_active(self):
        """
        The period is active if it has started but not ended yet.
        These inequations have to hold: start_date <= now < end_date.
        """
        return self.has_started() and not self.has_ended()
    is_active.boolean = True

    def is_paid(self):
        """
        True true if the paid_at field is set. If it is not set, the period
        has not been paid yet.
        """
        return self.paid_at is not None
    is_paid.boolean = True
