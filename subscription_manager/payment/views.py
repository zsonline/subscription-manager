# Django imports
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import CreateView
from django.utils.decorators import method_decorator

# Project imports
from subscription_manager.subscription.models import Subscription

# Application imports
from .forms import PaymentForm
from .models import Payment

@method_decorator(login_required, name='dispatch')
class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment/payment_create.html'
    subscription = None

    @classmethod
    def get_subscription(cls, **kwargs):
        """
        Read subscription id from URL parameters and return
        if subscription exists.
        """
        # Get from URL parameters
        subscription_id = kwargs.get('subscription_id')

        # Check if plan exists
        try:
            subscription = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            subscription = None

        return subscription

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method is called before get or post method.
        Checks if subscription exists and whether the user is eligible
        to renew it.
        """
        # Get subscription
        subscription = self.get_subscription(**kwargs)
        if subscription is None:
            # If subscription does not exist, return to list view and display
            # error message
            messages.error(request, 'Dieses Abonnement existiert nicht.')
            return redirect(reverse('subscription_list'))
        self.subscription = subscription

        # Check student eligibility
        if subscription.plan.slug == 'student' and \
                (not request.user.is_student() or Subscription.objects.has_student_subscriptions(request.user)):
            messages.error(request, 'Dieses Abonnement ist nur für Studenten.')
            return redirect(reverse('subscription_list'))

        # Check other eligibility
        if not subscription.expires_soon() or subscription.has_open_payments():
            messages.error(request, 'Dieses Abonnement kann nicht verlängert werden.')
            return redirect(reverse('subscription_list'))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, payment_form):
        """
        Sends confirmation email and redirects to
        appropriate page.
        """
        payment = self.object

        # Only set start and end date when subscription is free
        if payment.amount == 0:
            payment.confirm()
            messages.success(self.request, 'Vielen Dank! Du erhältst die ZS weiterhin nach Hause geliefert.')
            return redirect('subscription_list')

        # Send invoice
        payment.send_invoice()
        messages.success(self.request, 'Vielen Dank! Wir haben dir eine Rechnung per E-Mail geschickt.')
        return redirect('subscription_detail', subscription_id=payment.subscription.id)

    def get_form_kwargs(self):
        """
        Provide arguments for form initialisation
        so that the given price can be checked.
        """
        kwargs = super().get_form_kwargs()
        # Add min price to arguments
        kwargs['min_price'] = self.subscription.plan.price
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Adds subscription to template context.
        """
        data = super().get_context_data(**kwargs)
        data['subscription'] = self.subscription
        return data

    def get_initial(self):
        """
        Uses price of last payment. If no last payment exists,
        the initial plan price is used.
        """
        data = super().get_initial()
        # Load last payment
        last_payment = self.subscription.last_payment_amount()
        if last_payment is not None:
            data['amount'] = last_payment
        else:
            data['amount'] = self.subscription.plan.price
        return data