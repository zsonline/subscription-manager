from django.db import transaction
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import detail, edit, list

from subscription_manager.payment.forms import PaymentForm

from .admin import ActiveSubscriptionResource
from .forms import SubscriptionForm
from .models import Subscription, Plan, Period


@method_decorator(login_required, name='dispatch')
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
        if request.user.is_authenticated:
            subscription_form = SubscriptionForm(
                initial={
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name
                }
            )
        else:
            subscription_form = SubscriptionForm()
        payment_form = PaymentForm(
            plan=self.plan
        )

        return render(request, 'subscription/subscription_create.html', {
            'plan': self.plan,
            'subscription_form': subscription_form,
            'payment_form': payment_form
        })

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles post request. Validates form and creates
        subscription if data is valid.
        """
        # Get data from forms
        subscription_form = SubscriptionForm(data=request.POST)
        payment_form = PaymentForm(
            data=request.POST,
            plan=self.plan
        )

        # Validate other forms
        if subscription_form.is_valid() and payment_form.is_valid():
            # Save subscription
            subscription = subscription_form.save(commit=False)
            subscription.user = request.user
            subscription.plan = self.plan
            subscription.save()
            # Create period
            period = Period.objects.create(
                subscription=subscription,
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + self.plan.duration
            )
            # Save payment
            payment = payment_form.save(commit=False)
            payment.period = period
            payment.subscription = subscription
            payment.save()

            # Handle payment
            success = payment.handle()
            if success:
                if payment.amount == 0:
                    messages.success(request, 'Vielen Dank! Deine Bestellung war erfolgreich.')
                else:
                    messages.success(request, 'Vielen Dank für deine Bestellung! Wir haben dir eine Rechnung per E-Mail geschickt.')

            return redirect('login')

        return render(request, 'subscription/subscription_create.html', {
            'plan': self.plan,
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eligible_plans_pk = Plan.objects.filter_eligible(self.request.user).values('pk')
        context['not_eligible_plans'] = Plan.objects.filter(is_purchasable=True).exclude(pk__in=eligible_plans_pk)
        return context


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
        periods = Period.objects.filter(subscription=self.get_object()).order_by('-end_date')
        data['periods'] = periods
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
        if not subscription.is_active():
            raise Http404('Subscription is inactive')
        # Check if subscription is paid
        if not subscription.is_paid():
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
        messages.success(request, 'Dein Abo wurde gekündigt.')
        return HttpResponseRedirect(self.success_url)


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class SubscriptionExportView(View):
    """
    Supports the export of active subscriptions' addresses
    as .csv, .ods, and .xlsx documents.
    """
    format = 'csv'  # Default format is .csv

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method is called before get or post method.
        Checks if requested format is supported.
        """
        # Get format argument and check if it is supported. Otherwise,
        # raise 404 exception.
        format_arg = self.kwargs.get('format')
        if format_arg not in ['csv', 'ods', 'xlsx']:
            raise Http404()
        # Store format as class attribute
        self.format = format_arg

        return super().dispatch(request, *args, **kwargs)

    def content_type(self):
        """
        Return the format's corresponding content type.
        """
        if self.format == 'csv':
            return 'text/csv'
        elif self.format == 'ods':
            return 'application/vnd.oasis.opendocument.spreadsheet'
        elif self.format == 'xlsx':
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return ''

    def content(self):
        """
        Return the content formatted as the requested document.
        """
        if self.format == 'csv':
            return ActiveSubscriptionResource().export().csv
        elif self.format == 'ods':
            return ActiveSubscriptionResource().export().ods
        elif self.format == 'xlsx':
            return ActiveSubscriptionResource().export().xlsx
        return ''

    def get(self, request, *args, **kwargs):
        """
        Return the document as an attachement.
        """
        response = HttpResponse(
            content=self.content(),
            content_type=self.content_type()
        )
        response['Content-Disposition'] = 'attachment; filename="{}-active-subscriptions.{}"'.format(
            timezone.now().strftime('%Y-%m-%d'),
            self.format
        )
        return response


@method_decorator(login_required, name='dispatch')
class PeriodCreateView(View):
    subscription = None
    last_period = None

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method is called before get or post method.
        Checks if subscription exists and whether the user is eligible
        to renew it.
        """
        # Get from URL parameter
        subscription_id = kwargs.get('subscription_id')

        # Check if subscription exists
        try:
            subscription = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            raise Http404('Subscription does not exist.')

        # Check if it is the right user, she is eligible and the plan is renewable
        if not subscription.can_be_renewed_by(request.user):
            # If it is not the case, raise 404
            raise Http404('Subscription cannot be renewed.')

        self.subscription = subscription

        # Get last period
        self.last_period = self.subscription.period_set.order_by('-end_date').first()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Renders empty form on a get request.
        """
        # Initialise payment form
        initial_amount = self.subscription.plan.price
        if self.last_period is not None:
            initial_amount = self.last_period.payment.amount
        payment_form = PaymentForm(
            plan=self.subscription.plan,
            initial={
                'amount': initial_amount
            }
        )

        # Render template
        return render(request, 'subscription/period_create.html', {
            'subscription': self.subscription,
            'payment_form': payment_form
        })

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Sends confirmation email and redirects to
        appropriate page.
        """
        # Get data from form
        payment_form = PaymentForm(
            data=request.POST,
            plan=self.subscription.plan
        )

        # Validate other forms
        if payment_form.is_valid():
            # Renew subscription
            period = self.subscription.renew()
            # Save payment
            payment = payment_form.save(commit=False)
            payment.period = period
            payment.subscription = self.subscription
            payment.save()

            # Handle payment
            success = payment.handle()
            if success:
                if payment.amount == 0:
                    messages.success(request, 'Vielen Dank! Deine Bestellung war erfolgreich.')
                else:
                    messages.success(request,
                                     'Vielen Dank für deine Bestellung! Wir haben dir eine Rechnung per E-Mail geschickt.')

            return redirect('subscription_detail', subscription_id=self.subscription.pk)

        return render(request, 'subscription/period_create.html', {
            'subscription': self.subscription,
            'payment_form': payment_form
        })
