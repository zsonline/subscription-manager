# Django imports
from django.shortcuts import render, redirect, reverse, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

# Project imports
from subscription_manager.authentication.forms import SignUpForm

# Application imports
from .models import SubscriptionType
from .forms import SubscribeForm, AddressForm


def list_subscription_types_view(request):
    """
    Lists the subscriptions.
    """
    subscription_types = SubscriptionType.objects.all()
    return render(request, 'subscription/list_subscription_types.html', {'subscription_types': subscription_types})


def subscribe_view(request, slug):
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
        address_form = AddressForm(request.POST, prefix='address')

        if user_form.is_valid() and address_form.is_valid():

            # Save forms
            user_form.save()
            address_form.save()

            # If user does not exist, redirect to login page
            return redirect('login')

    # If it is another request, instantiate empty form
    else:
        user_form = SignUpForm(prefix='user')
        address_form = AddressForm(prefix='address')

    return render(request, 'subscription/subscribe.html', {
        'user_form': user_form,
        'address_form': address_form,
        'subscription_type': subscription_type
    })
