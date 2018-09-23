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
    form_class = PaymentForm
    template_name = 'payment/payment_create.html'
    subscription = None
    model = Payment


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
        self.subscription = subscription
        if subscription is None:
            # If subscription does not exist, return to list view and display
            # error message
            messages.error(request, 'Dieses Abonnement existiert nicht.')
            return redirect(reverse('subscription_list'))

        # Check eligibility
        if subscription.plan.slug == 'student' and \
                (not request.user.is_student() or Subscription.objects.has_student_subscriptions(request.user)):
            messages.error(request, 'Dieses Abonnement ist nur für Studenten.')
            return redirect(reverse('subscription_list'))

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['min_price'] = self.subscription.plan.price
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['subscription'] = self.subscription
        return data

    def get_initial(self):
        # TODO: use last paid price
        data = super().get_initial()
        data['amount'] = self.subscription.plan.price
        return data