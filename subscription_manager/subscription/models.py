from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from .managers import PlanManager, SubscriptionManager


class Plan(models.Model):
    """
    Model that holds the data for a plan (a type of subscription).
    Such a plan can or cannot be purchased by users.
    """
    name = models.CharField(
        max_length=50,
        verbose_name='Name'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Beschreibung'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug'
    )
    duration = models.DurationField(
        default=timezone.timedelta(days=365),
        verbose_name='Laufzeit'
    )
    price = models.PositiveIntegerField(
        verbose_name='Preis'
    )
    mode = models.CharField(
        max_length=6,
        choices=(
            ('auto', 'Automatisch'),
            ('manual', 'Manuell')
        ),
        default='auto',
        verbose_name='Verwaltungsmodus'
    )
    is_purchasable = models.BooleanField(
        default=True,
        verbose_name='Käuflich'
    )
    is_renewable = models.BooleanField(
        default=True,
        verbose_name='Erneuerbar'
    )
    renews_to = models.ForeignKey(
        to='self',
        on_delete=models.PROTECT,
        verbose_name='Erneuert als'
    )
    eligible_active_subscriptions_per_user = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name='Anzahl aktiver Abos pro Leserin',
        help_text='Kein Wert bedeutet, dass es keine Begrenzung gibt.'
    )
    eligible_email_domains = models.TextField(
        blank=True,
        default='',
        verbose_name='Berechtigte E-Mail-Domains',
        help_text='E-Mail-Adressen müssen mit einem Semikolon getrennt sein.'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Erstellt am'
    )

    class Meta:
        verbose_name = 'Abotyp'
        verbose_name_plural = 'Abotypen'

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

        # Converts list to string of comma- and conjunction-separated domains and returns it
        if len(eligible_email_domains) == 0:
            return ''
        elif len(eligible_email_domains) == 1:
            return eligible_email_domains[0]
        else:
            return ', '.join(eligible_email_domains[:-1]) + ' ' + conjunction + ' ' + eligible_email_domains[-1]

    def is_eligible(self, user=None):
        """
        Checks whether a given user is eligible
        to purchase the subscription.
        """
        if user is None or self in Plan.objects.filter_eligible(user):
            return True
        return False
    is_eligible.boolean = True


class Subscription(models.Model):
    """
    Model that holds the data for a user's subscription (an instance of a plan).
    A purchased plan corresponds to a subscription.
    """
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Account'
    )
    plan = models.ForeignKey(
        to='Plan',
        on_delete=models.PROTECT,
        verbose_name='Abotyp'
    )
    first_name = models.CharField(
        max_length=30,
        verbose_name='Vorname'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Nachname'
    )
    address_line = models.CharField(
        max_length=100,
        verbose_name='Adresse'
    )
    additional_address_line = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name='Adresszusatz'
    )
    postcode = models.CharField(
        max_length=8,
        verbose_name='Postleitzahl'
    )
    town = models.CharField(
        max_length=100,
        verbose_name='Ort'
    )
    country = models.CharField(
        max_length=50,
        default='Schweiz',
        verbose_name='Land'
    )
    canceled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Gekündigt am'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Erstellt am'
    )

    objects = SubscriptionManager()

    class Meta:
        verbose_name = 'Abo'
        verbose_name_plural = 'Abos'

    def __str__(self):
        return '{} #{} von {}'.format(self.plan, self.id, self.user.full_name)

    def _get_full_name(self):
        """
        Returns the subscriber's full name.
        """
        return '{} {}'.format(self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def is_canceled(self):
        """
        Returns true if the canceled_at field is set.
        """
        return self.canceled_at is not None
    is_canceled.boolean = True

    def is_active(self):
        """
        Returns true if the subscription has not been
        canceled and one active period exists.
        """
        return not self.is_canceled() and self.objects.filter_active_periods().count() == 1
    is_active.boolean = True

    def renew(self):
        """
        Renews the subscription by the duration of the plan.
        """
        # TODO:
        self.end_date += relativedelta(months=self.plan.duration)
        self.save()
        return self

    def has_open_payments(self):
        """
        Returns true if at least one payment associated with
        this subscription is open. Otherwise false.
        """
        # TODO:
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
        """
        # TODO:
        try:
            last_payment = self.payment_set.latest('created_at')
        except ObjectDoesNotExist:
            return None
        return last_payment.amount

    def expires_in_lt(self, days):
        """
        Returns true if subscription expires in less than
        the given amount of days.
        """
        # TODO:
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


# TODO: Enforce non-overlapping periods with constraints (Django 2.2)
class Period(models.Model):
    """
    Model that holds the data of a period. A period is one cycle of a user's
    subscription. If a user renews her subscription, a new period is created
    for that subscription.
    """
    subscription = models.ForeignKey(
        to='Subscription',
        on_delete=models.CASCADE,
        verbose_name='Abonnement'
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Anfangsdatum'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Enddatum'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Erstellt am'
    )

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
        It has also to be paid.
        """
        return self.has_started() and not self.has_ended() and self.payment.is_paid()
    is_active.boolean = True
