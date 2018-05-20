# Pip imports
from dateutil.relativedelta import relativedelta

# Django imports
from django.shortcuts import render, redirect, reverse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.views.generic.list import ListView

# Project imports
from subscription_manager.authentication.forms import SignUpForm
from subscription_manager.payment.models import Payment
from subscription_manager.payment.forms import MinimumPaymentForm

# Application imports
from .models import Subscription
from .forms import AddressWithNamesForm, AddressWithoutNamesForm
from .plans import Plans


def list_plans(request):
    """
    Lists all plans.
    """
    return render(request, 'subscription/plan_list.html', {'plans': Plans.data})


def purchase_view(request, slug):
    """

    """
    # Check if plan exists
    if slug not in Plans.slugs():
        # If plan does not exist, return to list view and display
        # error message
        messages.error(request, 'Das Angebot \"{}\" existiert nicht.'.format(slug))
        return redirect(reverse('list_plans'))

    # Get current plan
    plan = Plans.get(slug)

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
        # Payment form in case, the price is not fixed
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
        'user_form': user_form,
        'address_form': address_form,
        'payment_form': payment_form
    })


def home_view(request):
    """
    Login home view. For test purposes.
    """
    return HttpResponse(request.user.email)


class SubscriptionListView(ListView):
    model = Subscription
    context_object_name = 'subscriptions'
    template_name = 'subscription/subscription_list.html'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
