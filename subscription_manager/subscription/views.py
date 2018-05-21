# Pip imports
from dateutil.relativedelta import relativedelta

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import detail, edit, list

# Project imports
from subscription_manager.authentication.decorators import anonymous_required
from subscription_manager.authentication.forms import SignUpForm
from subscription_manager.payment.forms import MinimumPaymentForm
from subscription_manager.payment.models import Payment

# Application imports
from .forms import AddressWithNamesForm, AddressWithoutNamesForm
from .models import Subscription, Address
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
        address_form = AddressWithoutNamesForm(request.POST, prefix='address')
        if 'allow_different_name' in plan:
            address_form = AddressWithNamesForm(request.POST, prefix='address')

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
        address_form = AddressWithoutNamesForm(prefix='address')
        if 'allow_different_name' in plan:
            address_form = AddressWithNamesForm(prefix='address')

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
        Returns subscription object if it is owned
        by the current user and does exist. Otherwise,
        a 404 exception.
        """
        # Url parameter
        subscription_id = self.kwargs['subscription_id']
        # Get object from database
        return get_object_or_404(Subscription, id=subscription_id, user=self.request.user)


@method_decorator(login_required, name='dispatch')
class SubscriptionCreateView(edit.CreateView):
    model = Subscription
    fields = ['address']
    template_name = 'subscription/subscription_create.html'


@method_decorator(login_required, name='dispatch')
class SubscriptionUpdateView(edit.UpdateView):
    model = Address
    fields = ['first_name', 'last_name', 'address_line_1', 'address_line_2', 'postcode', 'city', 'country']
    template_name = 'subscription/subscription_update.html'
    success_url = reverse_lazy('subscription_list')

    def get_object(self, queryset=None):
        """
        Returns address object for a subscription id. If
        the subscription is not owned by the current user or
        does not exist, the user is redirected to the subscription
        list page.
        """
        # Get subscription object
        try:
            subscription = Subscription.objects.get(pk=self.kwargs['subscription_id'])
        except Subscription.DoesNotExist:
            # Redirect to subscription list if subscription does not exist
            return None

        # If subscription is not owned by current user, redirect
        if self.request.user != subscription.user:
            # Redirect to subscription list
            messages.error(self.request, 'Dieses Abo existiert nicht.')
            return redirect(reverse('subscription_list'))

        # Return address
        return subscription.address


@method_decorator(login_required, name='dispatch')
class SubscriptionDeleteView(edit.DeleteView):
    model = Subscription
    success_url = reverse_lazy('subscription_list')
    context_object_name = 'subscription'
    template_name = 'subscription/subscription_delete.html'

    def get_object(self, queryset=None):
        """
        Returns subscription object if it is owned
        by the current user and does exist. Otherwise,
        a 404 exception.
        """
        # Url parameter
        subscription_id = self.kwargs['subscription_id']
        # Get object from database
        return get_object_or_404(Subscription, id=subscription_id, user=self.request.user)
