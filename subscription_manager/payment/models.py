from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from subscription_manager.subscription.models import Subscription

from .managers import PaymentManager


class Payment(models.Model):
    period = models.OneToOneField(
        to='subscription.Period',
        on_delete=models.CASCADE,
        verbose_name='Abo'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Betrag in CHF'
    )
    method = models.CharField(
        max_length=20,
        choices=(
            ('invoice', 'Rechnung'),
            ('twint', 'Twint')
        ),
        default='invoice',
        verbose_name='Zahlungsmethode'
    )
    code = models.CharField(
        max_length=12,
        unique=True
    )
    paid_amount = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Bezahlter Betrag'
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        verbose_name='Bezahlt am'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Erstellt am'
    )

    objects = PaymentManager()

    class Meta:
        verbose_name = 'Zahlung'
        verbose_name_plural = 'Zahlungen'

    def __str__(self):
        return 'Zahlung für Abo {} von {}'.format(self.period.subscription.id, self.period.subscription.full_name)

    def is_paid(self):
        return self.paid_at is not None
    is_paid.boolean = True

    def pay_until(self):
        return (self.created_at + relativedelta(days=30)).date()

    def is_renewal(self):
        return self.subscription.start_date is not None

    def send_invoice(self):
        """
        Sends an email that contains the payment details
        for this payment.
        """
        if not self.is_renewal():
            template = 'emails/invoice_new.txt'
        else:
            template = 'emails/invoice_renewal.txt'

        send_mail(
            subject=settings.EMAIL_SUBJECT_PREFIX + 'Rechnung',
            message=render_to_string(template, {
                'to_name': self.subscription.user.first_name,
                'payment': self
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.subscription.user.email],
            fail_silently=False
        )

    def confirm(self):
        """
        Confirms a payment by activating the subscription
        and sending a confirmation email.
        """
        # Confirm payment
        self.paid_at = timezone.now()
        self.save()

        # Adjust subscription details
        if not self.is_renewal():
            self.subscription.start_date = timezone.now().date()
            self.subscription.end_date = timezone.now().date() + relativedelta(months=self.subscription.plan.duration)
            subject = 'Abo aktiviert'
            template = 'emails/payment_confirmation_new.txt'
        else:
            self.subscription.end_date += relativedelta(months=self.subscription.plan.duration)
            subject = 'Abo verlängert'
            template = 'emails/payment_confirmation_renewal.txt'
        self.subscription.save()

        # Send confirmation email
        send_mail(
            subject=settings.EMAIL_SUBJECT_PREFIX + subject,
            message=render_to_string(template, {
                'to_name': self.subscription.user.first_name,
                'payment': self
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.subscription.user.email],
            fail_silently=False
        )
