# Pip imports
from dateutil.relativedelta import relativedelta
from formtools.wizard.views import SessionWizardView

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import detail, edit, list

# Project imports
from subscription_manager.authentication.forms import SignUpForm
from subscription_manager.authentication.decorators import anonymous_required
from subscription_manager.payment.forms import PaymentForm
from subscription_manager.payment.models import Payment
from subscription_manager.utils.language import humanize_list

# Application imports
from .forms import SubscriptionForm
from .models import Subscription, Plan


class SubscriptionCreateWizard(SessionWizardView):
    template_name = 'subscription/subscription_create.html'
    form_list = [SignUpForm, SubscriptionForm, PaymentForm]
    plan = None

    def dispatch(self, request, *args, **kwargs):
        """
        Check whether a given plan exists.
        If not, redirect to plan list.
        """
        # Check if plan exists
        self.plan = self.get_plan()
        if self.plan is None:
            # Redirect if plan does not exist
            return redirect('plan_list')

        return super().dispatch(request, *args, **kwargs)

    def get_plan(self):
        """
        Read plan slug from URL parameters and return
        if it exists.
        """
        # Get from URL parameters
        plan_slug = self.kwargs.get('plan_slug')

        # Check if plan exists
        try:
            plan = Plan.objects.get(slug=plan_slug)
        except Plan.DoesNotExist:
            plan = None

        return plan

    def get_form_initial(self, step):
        """
        Add initial form data.
        """
        initial = super().get_form_initial(step)

        # Payment form
        if step == '2':
            initial['amount'] = self.get_plan().price

        return initial

    def get_form_kwargs(self, step=None):
        """
        Add form kwargs.
        """
        kwargs = super().get_form_kwargs(step)

        # Add plan
        kwargs['plan'] = self.get_plan()

        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        context['plan'] = self.plan

        return context


    def done(self, form_list, **kwargs):
        return HttpResponse([form.cleaned_data for form in form_list])


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
class SubscriptionCreateView(View):
    form_class = SubscriptionForm
    template_name = 'subscription/subscription_create1.html'

    @classmethod
    def get_plan(cls, **kwargs):
        """
        Read plan slug from URL parameters and return
        if plan exists.
        """
        # Get from URL parameters
        plan_slug = kwargs.get('plan_slug')

        # Check if plan exists
        try:
            plan = Plan.objects.get(slug=plan_slug)
        except Plan.DoesNotExist:
            plan = None

        return plan

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method is called before get or post method.
        Checks if plan exists and whether the user is eligible
        to buy a subscription of that plan.
        """
        # Get plan
        plan = self.get_plan(**kwargs)
        if plan is None:
            # If plan does not exist, return to list view and display
            # error message
            messages.error(request, 'Das Abonnement existiert nicht.')
            return redirect('plan_list')

        # Check eligibility
        if plan.slug == 'student' and \
                (not request.user.is_student() or Subscription.objects.has_student_subscriptions(request.user)):
            messages.error(request, 'Dein gewähltes Abonnement ist nur für ETH-Studierende ({}). Darum kannst du es nicht abonnieren. Wähle stattdessen ein anderes Abo.'
                           .format(humanize_list(['@' + s for s in settings.ALLOWED_STUDENT_EMAIL_ADDRESSES], 'oder')))
            return redirect('plan_list')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles get request. Renders empty form.
        """
        # Get plan (already checked in dispatch method)
        plan = self.get_plan(**kwargs)

        # Forms
        subscription_form = SubscriptionForm()
        payment_form = PaymentForm(
            min_price=plan.price,
            initial={
                'amount': plan.price
            }
        )

        return render(request, 'subscription/subscription_create1.html', {
            'plan': plan,
            'subscription_form': subscription_form,
            'payment_form': payment_form
        })

    def post(self, request, *args, **kwargs):
        """
        Handles post request. Validates form and creates
        subscription if data is valid.
        """
        # Get plan (already checked in dispatch method)
        plan = self.get_plan(**kwargs)

        # Get data from forms
        subscription_form = SubscriptionForm(request.POST)
        payment_form = PaymentForm(
            request.POST,
            min_price=plan.price,
            initial={
                'amount': plan.price
            })

        # Validate forms
        if subscription_form.is_valid() and payment_form.is_valid():
            # Save subscription
            subscription = subscription_form.save(commit=False)
            subscription.user = request.user
            subscription.plan = plan
            subscription.save()
            # Save payment
            payment = payment_form.save(commit=False)
            payment.subscription = subscription
            payment.save()

            # Only set start and end date when subscription is free
            if payment.amount == 0:
                payment.confirm()
                messages.success(request, 'Vielen Dank! Ab sofort erhältst du die ZS nach Hause geliefert.')
                return redirect('subscription_list')

            # Send invoice
            payment.send_invoice()
            messages.success(request, 'Vielen Dank! Wir haben dir eine Rechnung per E-Mail geschickt.')
            return redirect('subscription_detail', subscription_id=subscription.id)

        return render(request, 'subscription/subscription_create1.html', {
            'plan': plan,
            'subscription_form': subscription_form,
            'payment_form': payment_form
        })


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
