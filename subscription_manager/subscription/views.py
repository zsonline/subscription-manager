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

        user_form = SignUpForm(request.POST, prefix='user')
        if subscription_type.allow_other_name:
            address_form = AddressForm(request.POST, prefix='address')
        else:
            address_form = AddressWithoutNamesForm(request.POST, prefix='address')

        if user_form.is_valid() and address_form.is_valid():

            # Save forms
            user = user_form.save()
            address = address_form.save()

            # Initialise values for other models
            price = subscription_type.price
            paid_at = None
            start_date = None
            if price == 0:
                paid_at = timezone.now()
                start_date = timezone.now()

            # Create and save payment
            payment = Payment.objects.create(
                amount=price,
                paid_at=paid_at
            )

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
        user_form = SignUpForm(prefix='user')
        if subscription_type.allow_other_name:
            address_form = AddressForm(prefix='address')
        else:
            address_form = AddressWithoutNamesForm(prefix='address')

    return render(request, 'subscription/purchase.html', {
        'user_form': user_form,
        'address_form': address_form,
        'subscription_type': subscription_type
    })
