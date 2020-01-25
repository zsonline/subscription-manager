from random import randint
from post_office import mail

from django.conf import settings
from django.db import models, IntegrityError, transaction
from django.template.loader import render_to_string
from django.utils import timezone

from subscription_manager.subscription.models import Period, Subscription

from .managers import PaymentManager


class Payment(models.Model):
    period = models.OneToOneField(
        to=Period,
        on_delete=models.CASCADE,
        verbose_name='Periode'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Betrag in CHF'
    )
    method = models.CharField(
        max_length=20,
        choices=(
            ('invoice', 'Banküberweisung'),
            # ('twint', 'Twint')
        ),
        default='invoice',
        verbose_name='Zahlungsmethode'
    )
    code = models.CharField(
        max_length=12,
        unique=True
    )
    due_on = models.DateField(
        verbose_name='Zahlbar bis'
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
        return 'Zahlung für Abo {} von {}'.format(self.period.subscription.id, self.period.subscription.user.full_name())

    def is_paid(self):
        """
        Returns true if the paid at datetime is set.
        """
        return self.paid_at is not None
    is_paid.boolean = True

    def is_renewal(self):
        """
        Returns true if the payment is for a renewal.
        """
        return self.period.subscription.period_set.count() > 1
    is_renewal.boolean = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Overrides the save method. If the object is newly created,
        generate a code and set the due on date.
        """
        # If object is newly created
        if not self.pk:
            # Set due on date
            self.due_on = timezone.now().date() + timezone.timedelta(days=30)

            # Generate code
            while True:
                try:
                    code = 'ZS-' + str(randint(1000, 9999)) + '-' + str(randint(1000, 9999))
                    self.code = code
                    # Try creating the payment object
                    with transaction.atomic():
                        super().save(force_insert, force_update, using, update_fields)
                except IntegrityError:
                    continue
                break

        # If object existed already
        else:
            super().save(force_insert, force_update, using, update_fields)

    def handle(self):
        """
        Handles the payment by sending an invoice via email
        if the amount is not zero. Would also handle other
        payment methods.
        """
        # If purchase was for free, confirm payment
        if self.amount == 0:
            self.confirm()
            return True

        # Send invoice via email
        if self.method == 'invoice':
            self.send_invoice()
            return True

        # All other payment methods are not yet supported
        return False

    def send_invoice(self):
        """
        Sends an email that contains the payment details
        for this payment.
        """
        if not self.is_renewal():
            # New subscription
            template = 'emails/payment_invoice_new.txt'
        else:
            # Renewal subscription
            template = 'emails/payment_invoice_renewal.txt'

        # Add accounting emails to recipient list
        recipient_list = [self.period.subscription.user.email]
        recipient_list += settings.ACCOUNTING_EMAIL

        mail.send(
            subject=settings.EMAIL_SUBJECT_PREFIX + 'Rechnung',
            message=render_to_string(template, {
                'to_name': self.period.subscription.user.first_name,
                'payment': self
            }),
            recipients=recipient_list,
            priority='middle'
        )

    def confirm(self):
        """
        Confirms a payment by activating the subscription
        and sending a confirmation email.
        """
        # Confirm payment
        self.paid_at = timezone.now()
        self.save()

        # Adjust period interval if payment is received after already set start date
        if self.paid_at.date() > self.period.start_date:
            self.period.start_date = self.paid_at.date()
            self.period.end_date = (self.paid_at + self.period.subscription.plan.duration).date()
            self.period.save()

        if not self.is_renewal():
            # New subscription
            subject = 'Abo aktiviert'
            template = 'emails/payment_confirmation_new.txt'
        else:
            # Renewal subscription
            subject = 'Abo verlängert'
            template = 'emails/payment_confirmation_renewal.txt'

        # Send confirmation email
        mail.send(
            subject=settings.EMAIL_SUBJECT_PREFIX + subject,
            message=render_to_string(template, {
                'to_name': self.period.subscription.user.first_name,
                'payment': self
            }),
            recipients=[self.period.subscription.user.email],
            priority='middle'
        )
