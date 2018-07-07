# Pip imports
from dateutil.relativedelta import relativedelta

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import detail, edit, list

# Project imports
from subscription_manager.authentication.decorators import anonymous_required
from subscription_manager.authentication.forms import SignUpForm
from subscription_manager.payment.forms import MinimumPaymentForm
from subscription_manager.payment.models import Payment

# Application imports
from .forms import SubscriptionWithNamesForm, SubscriptionWithoutNamesForm
from .models import Subscription
from .plans import Plans


@anonymous_required
def plan_list_view(request):
    """
    Lists all plans.
    """
    return render(request, 'subscription/plans.html', {'plans': Plans.data})


@anonymous_required
def purchase_view(request, plan_slug):
    """
    Displays a form for opening a new account and
    purchasing a subscription.
    """
    # Check if plan exists
    if plan_slug not in Plans.slugs():
        # If plan does not exist, return to list view and display
        # error message
        messages.error(request, 'Das Angebot \"{}\" existiert nicht.'.format(plan_slug))
        return redirect(reverse('plans'))

    # Get current plan
    plan = Plans.get(plan_slug)

    # For POST requests, process the form data
    if request.method == 'POST':

        # Get data from user form
        user_form = SignUpForm(request.POST, prefix='user')

        # Get data from right address form
        address_form = SubscriptionWithoutNamesForm(request.POST, prefix='address')
        if 'allow_different_name' in plan:
            address_form = SubscriptionWithNamesForm(request.POST, prefix='address')

        payment_form = None
        # Payment form in case of a dynamic price
        if 'min_price' in plan:
            payment_form = MinimumPaymentForm(
                request.POST,
                prefix='payment',
                min_price=plan['min_price'],
                initial={
                    'amount': plan['min_price']
                }
            )

        # Validate forms
        if user_form.is_valid() and address_form.is_valid() and (payment_form is None or payment_form.is_valid()):
            # Save forms
            user = user_form.save()
            address = address_form.save()
            if payment_form is not None:
                payment = payment_form.save()
            else:
                payment = Payment.objects.create(amount=plan['price'])

            # Create and save subscription
            Subscription.objects.create(
                user=user,
                plan=plan['slug'],
                address=address,
                payment=payment,
                start_date=timezone.now(),
                end_date=timezone.now() + relativedelta(months=+plan['duration'])
            )

            # TODO: Send email

            messages.success(request, 'Abonnement-Kauf erfolgreich.')
            return redirect('login')

    # If it is another request, instantiate empty form
    else:

        # User form
        user_form = SignUpForm(prefix='user')

        # Choose right address form
        address_form = SubscriptionWithoutNamesForm(prefix='address')
        if 'allow_different_name' in plan:
            address_form = SubscriptionWithNamesForm(prefix='address')

        payment_form = None
        # Payment form in case the price is not fixed
        if 'min_price' in plan:
            payment_form = MinimumPaymentForm(
                prefix='payment',
                min_price=plan['min_price'],
                initial={
                    'amount': plan['min_price']
                }
            )

    return render(request, 'subscription/purchase.html', {
        'plan': plan,
        'address_form': address_form,
        'payment_form': payment_form,
        'user_form': user_form
    })


@method_decorator(login_required, name='dispatch')
class PlanListView(list.ListView):
    """
    Lists all subscriptions of the current user.
    """
    context_object_name = 'plans'
    template_name = 'subscription/plan_list.html'

    def get_queryset(self):
        return Plans.data


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
        if subscription.payment.is_paid():
            raise Http404('Subscription is paid')
        return subscription


@method_decorator(login_required, name='dispatch')
class SubscriptionCreateView(View):
    form_class = SubscriptionWithNamesForm
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
        if plan_slug not in Plans.slugs():
            return None

        return Plans.get(plan_slug)

    def get(self, request, *args, **kwargs):
        """
        Handles get request. Renders empty form.
        """
        # Get plan
        plan = self.get_plan(**kwargs)
        if plan is None:
            # If plan does not exist, return to list view and display
            # error message
            messages.error(request, 'Dieses Abonnement existiert nicht.')
            return redirect(reverse('subscription_list'))

        # Choose right subscription form
        subscription_form = SubscriptionWithoutNamesForm(prefix='address')
        if 'allow_different_name' in plan:
            subscription_form = SubscriptionWithNamesForm(prefix='address')

        payment_form = None
        # Payment form in case the price is not fixed
        if 'min_price' in plan:
            payment_form = MinimumPaymentForm(
                prefix='payment',
                min_price=plan['min_price'],
                initial={
                    'amount': plan['min_price']
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
        # Get plan
        plan = self.get_plan(**kwargs)
        if plan is None:
            # If plan does not exist, return to list view and display
            # error message
            messages.error(request, 'Dieses Abo existiert nicht.')
            return redirect(reverse('subscription_list'))

        # Get data from right subscription form
        subscription_form = SubscriptionWithoutNamesForm(request.POST, prefix='address')
        if 'allow_different_name' in plan:
            subscription_form = SubscriptionWithNamesForm(request.POST, prefix='address')

        payment_form = None
        # Payment form in case of a dynamic price
        if 'min_price' in plan:
            payment_form = MinimumPaymentForm(
                request.POST,
                prefix='payment',
                min_price=plan['min_price'],
                initial={
                    'amount': plan['min_price']
                }
            )

        # Validate forms
        if subscription_form.is_valid() and (payment_form is None or payment_form.is_valid()):
            # Save payment
            if payment_form is not None:
                payment = payment_form.save()
            else:
                payment = Payment.objects.create(amount=plan['price'])
            # Save subscription
            subscription = subscription_form.save(commit=False)
            subscription.user = request.user
            subscription.plan = plan['slug']
            subscription.payment = payment
            subscription.start_date = timezone.now()
            subscription.end_date = timezone.now() + relativedelta(months=+plan['duration'])
            subscription.save()

            messages.success(request, 'Abo-Kauf erfolgreich. Danke!')
            return redirect('subscription_list')

        return render(request, 'subscription/subscription_create.html', {
            'plan': plan,
            'subscription_form': subscription_form,
            'payment_form': payment_form
        })


@method_decorator(login_required, name='dispatch')
class SubscriptionUpdateView(edit.UpdateView):
    model = Subscription
    form_class = SubscriptionWithoutNamesForm
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
class SubscriptionDeleteView(edit.DeleteView):
    model = Subscription
    success_url = reverse_lazy('subscription_list')
    context_object_name = 'subscription'
    template_name = 'subscription/subscription_delete.html'

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
