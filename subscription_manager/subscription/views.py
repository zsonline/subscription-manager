# Pip imports
from dateutil.relativedelta import relativedelta

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import detail, edit, list

# Project imports
from subscription_manager.authentication.decorators import anonymous_required
from subscription_manager.payment.forms import PaymentForm
from subscription_manager.payment.models import Payment

# Application imports
from .forms import SubscriptionForm
from .models import Subscription, Plan


@method_decorator(login_required, name='dispatch')
class PlanListView(list.ListView):
    """
    Lists all subscriptions of the current user.
    """
    context_object_name = 'plans'
    template_name = 'subscription/plan_list.html'

    def get_queryset(self):
        """
        Excludes student plan if logged in user
        is not an eligible student.
        """
        if not self.request.user.is_student():
            return Plan.objects.filter(only_student=False)
        return Plan.objects.all()


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
    template_name = 'subscription/subscription_create.html'

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
            messages.error(request, 'Dieses Abonnement existiert nicht.')
            return redirect(reverse('plan_list'))

        # Check eligibility
        if plan.only_student and not request.user.is_student():
            messages.error(request, 'Dieses Abonnement ist nur für Studentinnen.')
            return redirect(reverse('plan_list'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles get request. Renders empty form.
        """
        # Get plan (already checked in dispatch method)
        plan = self.get_plan(**kwargs)

        # Choose right subscription form
        subscription_form = SubscriptionForm(prefix='address')

        payment_form = None
        # Payment form in case the price is not fixed
        if plan.is_min_price:
            payment_form = MinimumPaymentForm(
                prefix='payment',
                min_price=plan.price,
                initial={
                    'amount': plan.price
                }
            )

        return render(request, 'subscription/subscription_create.html', {
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

        # Get data from right subscription form
        subscription_form = SubscriptionForm(request.POST, prefix='address')

        payment_form = None
        # Payment form in case of a dynamic price
        if plan.is_min_price:
            payment_form = MinimumPaymentForm(
                request.POST,
                prefix='payment',
                min_price=plan.price,
                initial={
                    'amount': plan.price
                }
            )

        # Validate forms
        if subscription_form.is_valid() and (payment_form is None or payment_form.is_valid()):
            # Save subscription
            subscription = subscription_form.save(commit=False)
            subscription.user = request.user
            subscription.plan = plan
            subscription.save()
            # Save payment
            if payment_form is not None:
                payment = payment_form.save(commit=False)
                payment.subscription = subscription
                payment.save()
            else:
                payment = Payment.objects.create(subscription=subscription, amount=plan.price)

            # Only set start and end date when subscription is free
            if payment.amount == 0:
                subscription.start_date = timezone.now()
                subscription.end_date = timezone.now() + relativedelta(months=+plan.duration)
                subscription.save()

            # Make a context variable for the templates
            context = {
                'to_name': request.user.first_name,
                'from_name': settings.ORGANISATION_NAME,
                'subscription': subscription
            }
            # Render the content templates
            text_content = render_to_string('subscription/emails/purchase_confirmation.txt', context)
            html_content = render_to_string('subscription/emails/purchase_confirmation.html', context)
            # Create the text and html version of the email
            message = EmailMultiAlternatives(
                subject='Token',
                body=text_content,
                from_email=settings.ORGANISATION_FROM_EMAIL,
                to=[request.user.email],
                headers={
                    'Reply-To': settings.ORGANISATION_REPLY_TO_EMAIL
                }
            )
            message.attach_alternative(html_content, 'text/html')
            # Send the email
            message.send()

            messages.success(request, 'Abo gekauft.')
            return redirect('subscription_list')

        return render(request, 'subscription/subscription_create.html', {
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
