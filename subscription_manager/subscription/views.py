from django.db import transaction
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import detail, edit, list

from subscription_manager.authentication.forms import SignUpForm
from subscription_manager.authentication.models import Token
from subscription_manager.payment.forms import PaymentForm
from subscription_manager.payment.models import Payment

from .forms import SubscriptionForm
from .models import Subscription, Plan, Period


class SubscriptionCreateView(View):
    plan = None
    template_name = 'subscription/subscription_create.html'

    def get_plan(self):
        """
        Read plan slug from URL parameters and return if it exists.
        """
        # Get from URL parameters
        plan_slug = self.kwargs.get('plan_slug')

        # Check if plan exists
        try:
            plan = Plan.objects.get(slug=plan_slug)
        except Plan.DoesNotExist:
            plan = None

        return plan

    def dispatch(self, request, *args, **kwargs):
        """
        Check whether a given plan exists and that the user is eligible
        to purchase the plan. If not, redirect to plan list.
        Remove signup form if a user is already logged in.
        """
        # Check if plan exists
        self.plan = self.get_plan()
        if self.plan is None:
            # Redirect if plan does not exist
            return redirect('plan_list')

        # Check if the user is allowed to purchase the plan
        user = request.user
        if not self.plan.is_eligible(user):
            messages.error(request, 'Du bist nicht berechtigt, dieses Abo zu bestellen.')
            return redirect('plan_list')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Renders empty forms on a get request.
        """
        signup_form = None
        if not request.user.is_authenticated:
            signup_form = SignUpForm(
                plan=self.plan
            )
        subscription_form = SubscriptionForm()
        payment_form = PaymentForm(
            plan=self.plan
        )

        return render(request, 'subscription/subscription_create.html', {
            'plan': self.plan,
            'signup_form': signup_form,
            'subscription_form': subscription_form,
            'payment_form': payment_form
        })

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles post request. Validates form and creates
        subscription if data is valid.
        """
        has_error = False

        # Get data from forms
        signup_form = None
        subscription_form = SubscriptionForm(data=request.POST)
        payment_form = PaymentForm(
            data=request.POST,
            plan=self.plan
        )

        # Create user if she is not already logged in
        user = request.user
        if not user.is_authenticated:
            signup_form = SignUpForm(
                data=request.POST,
                plan=self.plan
            )

            if signup_form.is_valid():
                user = signup_form.save()
            else:
                has_error = True

        # Validate other forms
        if not has_error and subscription_form.is_valid() and payment_form.is_valid():
            # Save subscription
            subscription = subscription_form.save(commit=False)
            subscription.user = user
            subscription.plan = self.plan
            subscription.save()
            # Create period
            period = Period.objects.create(
                subscription=subscription,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + self.plan.duration,
                email_confirmed=self.plan.eligible_email_domains is None
            )
            # Save payment
            payment = payment_form.save(commit=False)
            payment.period = period
            payment.save()

            # Send email verification email
            if not period.email_confirmed:
                Token.objects.create_and_send()
                messages.info(request, 'Wir haben dir eine E-Mail geschickt, um deine E-Mail-Adresse zu verifizieren.')

            # Handle payment
            if payment.amount == 0:
                payment.confirm()
                messages.success(request, 'Vielen Dank! Deine Bestellung war erfolgreich.')
            else:
                payment.send_invoice()
                messages.success(request,
                                 'Vielen Dank für deine Bestellung! Wir haben dir eine Rechnung per E-Mail geschickt.')

            return redirect('login')

        return render(request, 'subscription/subscription_create.html', {
            'plan': self.plan,
            'signup_form': signup_form,
            'subscription_form': subscription_form,
            'payment_form': payment_form
        })


class PlanListView(list.ListView):
    """
    Lists all plans for which the user can potentially purchase.
    """
    context_object_name = 'plans'
    template_name = 'subscription/plan_list.html'

    def get_queryset(self):
        """
        Returns only plans for which the user is potentially eligible.
        """
        return Plan.objects.filter_eligible(self.request.user)


@method_decorator(login_required, name='dispatch')
class SubscriptionListView(list.ListView):
    """
    Lists all subscriptions of the current user.
    """
    model = Subscription
    context_object_name = 'subscriptions'
    template_name = 'subscription/subscription_list.html'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class SubscriptionDetailView(detail.DetailView):
    """
    Detail view of a subscription. Shows mainly payment
    details.
    """
    model = Subscription
    context_object_name = 'subscription'
    template_name = 'subscription/subscription_detail.html'

    def get_object(self, queryset=None):
        """
        Returns subscription object if it is not paid, owned
        by the current user and does exist. Otherwise,
        a 404 exception.
        """
        # Parameters
        subscription_id = self.kwargs['subscription_id']
        user = self.request.user
        # Get object or raise 404
        subscription = get_object_or_404(Subscription, id=subscription_id, user=user)
        return subscription

    def get_context_data(self, **kwargs):
        """
        Adds all associated payments to the context.
        """
        data = super().get_context_data(**kwargs)
        payments = Payment.objects.filter(subscription=self.get_object())
        data['payments'] = payments
        return data


@method_decorator(login_required, name='dispatch')
class SubscriptionUpdateView(edit.UpdateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscription/subscription_update.html'
    success_url = reverse_lazy('subscription_list')

    def get_object(self, queryset=None):
        """
        Returns subscription object if it is active, owned
        by the current user and does exist. Otherwise,
        a 404 exception.
        """
        subscription_id = self.kwargs['subscription_id']
        user = self.request.user
        # Get object or raise 404
        subscription = get_object_or_404(Subscription, id=subscription_id, user=user)
        # Check if subscription is active
        if not subscription.is_active():
            raise Http404('Subscription is inactive')
        return subscription


@method_decorator(login_required, name='dispatch')
class SubscriptionCancelView(edit.DeleteView):
    model = Subscription
    success_url = reverse_lazy('subscription_list')
    context_object_name = 'subscription'
    template_name = 'subscription/subscription_cancel.html'

    def get_object(self, queryset=None):
        """
        Returns subscription object if it is active, owned
        by the current user and does exist. Otherwise,
        a 404 exception.
        """
        subscription_id = self.kwargs['subscription_id']
        user = self.request.user
        # Get object or raise 404
        subscription = get_object_or_404(Subscription, id=subscription_id, user=user)
        # Check if subscription is active
        if not subscription.is_active() or subscription.has_open_payments():
            raise Http404('Subscription is inactive')
        return subscription

    def delete(self, request, *args, **kwargs):
        """
        Overwrites delete method to only cancel the subscription
        and not delete it.
        """
        subscription = self.get_object()
        subscription.canceled_at = timezone.now()
        subscription.save()
        return HttpResponseRedirect(self.success_url)
