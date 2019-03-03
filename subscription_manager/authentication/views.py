# Django imports
from django.shortcuts import render, redirect, reverse, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Project imports
from subscription_manager.subscription.models import Plan

# Application imports
from .models import Token
from .forms import SignUpForm, LoginForm
from .decorators import anonymous_required


@anonymous_required
def signup_view(request):
    """
    Renders or processes the signup form through which
    a user can register himself.
    """
    # Read next parameter
    next_page = request.GET.get('next')

    # For POST requests, process the form data
    if request.method == 'POST':

        form = SignUpForm(request.POST)

        if form.is_valid():

            # Save user
            user = form.save()

            # If successful
            if user is not None:
                # Create and send verification token
                Token.objects.create_and_send(user=user, action='signup', next_page=next_page)
                # Create success message
                messages.success(request, 'Wir haben dir eine E-Mail geschickt, '
                                          'um deine E-Mail-Adresse zu verfizieren.')
                # Redirect to this page
                return redirect('login')

            # If user does not exist, display error
            form.add_error(None, 'Es ist ein Fehler aufgetreten. Dein Account konnte nicht erstellt werden.'
                                 'Bitte versuche es erneut.')

    # If it is another request, instantiate empty form
    else:
        form = SignUpForm()

    plans = Plan.objects.all()

    return render(request, 'authentication/signup.html', {'form': form, 'next': next_page, 'plans': plans})


@anonymous_required
def login_view(request):
    """
    Renders or processes the login form. If the data is valid,
    a token is sent and the user redirected to the token verification
    page. Otherwise, the login form is rendered.
    """
    # Read next parameter
    next_page = request.GET.get('next', None)

    # For POST requests, process the form data
    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            # Get user
            try:
                user = get_user_model().objects.get(email=form.cleaned_data['email'])
            except get_user_model().DoesNotExist:
                user = None

            # If user exists
            if user is not None:
                # Create and send token
                Token.objects.create_and_send(user=user, action='login', next_page=next_page)
                # Create success message
                messages.success(request, 'Wir haben dir einen Login-Link per E-Mail geschickt.'.format(user.email))
                # Redirect to this page
                return redirect('login')

    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {'form': form, 'next': next_page})


def token_verification_view(request, code):
    """
    Checks login token. If the token is valid, the user is
    redirected to the login home page. If not, she is being
    redirected to the login page and an error is displayed.
    """
    token = Token.objects.get_from_code(code)
    if token is None:
        messages.error(request, 'Dein Link ist ungültig.')
        return redirect('login')

    # Authenticate
    user = authenticate(code=code)
    # If authentication is successful, log user in
    if user is not None:
        login(request, user)
        if token.action == 'signup':
            messages.success(request, 'Deine E-Mail-Adresse wurde bestätigt.')
        elif token.action == 'login':
            messages.success(request, 'Du bist eingeloggt.')
        # Handle next parameter
        next_page = request.GET.get('next', None)
        if next_page is not None:
            return redirect(next_page)
        # Redirect user to login home otherwise
        return redirect(settings.LOGIN_REDIRECT_URL)

    messages.error(request, 'Der Anmelde- oder Bestätigungs-Link ist ungültig. Fordere einen Neuen an.')
    return redirect('login')


@login_required(redirect_field_name=None)
def logout_view(request):
    """
    Logs a user out and redirects her to the login page.
    """
    logout(request)
    messages.success(request, 'Du wurdest abgemeldet.')
    return redirect('login')
