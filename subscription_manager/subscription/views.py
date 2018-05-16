# Django imports
from django.shortcuts import render, redirect, reverse, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Project imports
from subscription_manager.authentication.forms import SignUpForm
from subscription_manager.payment.models import Payment
from subscription_manager.payment.forms import PaymentForm

# Application imports
from .models import SubscriptionType, Subscription
from .forms import AddressForm, AddressWithoutNamesForm


def list_subscription_types_view(request):
    """
    Lists the subscriptions.
    """
    subscription_types = SubscriptionType.objects.all()
    return render(request, 'subscription/list_subscription_types.html', {'subscription_types': subscription_types})


def purchase_view(request, slug):
    """

    """
    # Load subscription type from database. If it does not
    # exist, redirect to list view
    try:
        subscription_type = SubscriptionType.objects.get(slug=slug)
    except SubscriptionType.DoesNotExist:
        return redirect('list_subscription_types')

    # For POST requests, process the form data
    if request.method == 'POST':

        # Get data from user form
        user_form = SignUpForm(request.POST, prefix='user')
        # Get data from right address form
        if subscription_type.allow_other_name:
            address_form = AddressForm(request.POST, prefix='address')
        else:
            address_form = AddressWithoutNamesForm(request.POST, prefix='address')
        # Get data from payment form
        if subscription_type.fixed_price:
            payment_form = PaymentForm(
                request.POST,
                prefix='payment',
                initial={
                    'amount': subscription_type.price
                },
            )
        else:
            payment_form = PaymentForm(request, prefix='payment')

        # Validate forms
        if user_form.is_valid() and address_form.is_valid() and payment_form.is_valid():
            # Save forms
            user = user_form.save()
            address = address_form.save()
            payment = payment_form.save()

            # Create start date
            start_date = None
            if payment.amount == 0:
                start_date = timezone.now()

            # Create and save subscription
            Subscription.objects.create(
                user=user,
                type=subscription_type,
                address=address,
                payment=payment,
                start_date=start_date
            )

            return redirect('login')

    # If it is another request, instantiate empty form
    else:

        # User form
        user_form = SignUpForm(prefix='user')
        # Choose right address form
        if subscription_type.allow_other_name:
            address_form = AddressForm(prefix='address')
        else:
            address_form = AddressWithoutNamesForm(prefix='address')
        # Payment form
        payment_form = PaymentForm(prefix='payment')

    return render(request, 'subscription/purchase.html', {
        'user_form': user_form,
        'address_form': address_form,
        'payment_form': payment_form,
        'subscription_type': subscription_type
    })
