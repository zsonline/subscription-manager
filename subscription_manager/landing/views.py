# Pip imports
from dateutil.relativedelta import relativedelta

# Django imports
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import list
from django.utils import timezone
from django.utils.decorators import method_decorator

# Project imports
from subscription_manager.authentication.forms import SignUpForm
from subscription_manager.authentication.decorators import anonymous_required
from subscription_manager.payment.forms import PaymentForm
from subscription_manager.subscription.forms import SubscriptionForm
from subscription_manager.subscription.models import Plan

# Application imports
from subscription_manager.subscription.views import PlanListView

@method_decorator(anonymous_required, name='dispatch')
class PlanSelection(list.ListView):
    model = Plan
    context_object_name = 'plans'
    template_name = 'landing/plan_list.html'


@method_decorator(anonymous_required, name='dispatch')
class Purchase(View):
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
            return redirect(reverse('index'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles get request. Renders empty form.
        """
        # Get plan (already checked in dispatch method)
        plan = self.get_plan(**kwargs)

        # Get forms
        user_form = SignUpForm()
        subscription_form = SubscriptionForm()
        payment_form = PaymentForm(
            min_price=plan.price,
            initial={
                'amount': plan.price
            }
        )

        return render(request, 'landing/purchase.html', {
            'plan': plan,
            'user_form': user_form,
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
        user_form = SignUpForm(request.POST)
        subscription_form = SubscriptionForm(request.POST)
        payment_form = PaymentForm(
            request.POST,
            min_price=plan.price,
            initial={
                'amount': plan.price
            })

        # Validate forms
        if user_form.is_valid() and subscription_form.is_valid() and payment_form.is_valid():
            # Save subscription
            user = user_form.save()
            subscription = subscription_form.save(commit=False)
            subscription.user = user
            subscription.plan = plan
            subscription.save()
            # Save payment
            payment = payment_form.save(commit=False)
            payment.subscription = subscription
            payment.save()

            # Only set start and end date when subscription is free
            # if payment.amount == 0:
            #     subscription.start_date = timezone.now()
            #     subscription.end_date = timezone.now() + relativedelta(months=+plan.duration)
            #     subscription.save()

            # Send email
            send_mail(
                '[ZS] Abonnement abgeschlossen',
                render_to_string('subscription/emails/purchase_confirmation.txt', {
                    'to_name': request.user.first_name,
                    'subscription': subscription
                }),
                settings.ORGANISATION_FROM_EMAIL,
                [request.user.email],
                fail_silently=False
            )

            messages.success(request, 'Abonnement abgeschlossen.')
            return redirect('login')

        return render(request, 'subscription/subscription_create.html', {
            'plan': plan,
            'subscription_form': subscription_form,
            'payment_form': payment_form
        })
