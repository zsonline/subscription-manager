from django.shortcuts import render, redirect, reverse, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import detail, edit, list
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import Http404

from subscription_manager.subscription.models import Plan

from .models import EmailAddress, Token, User
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
                Token.objects.create_and_send(email_address=user.primary_email, purpose='verification', next_page=next_page)
                # Create success message
                messages.success(request, 'Wir haben dir eine E-Mail geschickt, um deine E-Mail-Adresse zu verfizieren.')
                # Redirect to this page
                return redirect('login')

            # If user does not exist, display error
            form.add_error(None, 'Es ist ein Fehler aufgetreten. Dein Account konnte nicht erstellt werden.')

    # If it is another request, instantiate empty form
    else:
        form = SignUpForm()

    plans = Plan.objects.all()

    return render(request, 'user/signup.html', {'form': form, 'next': next_page, 'plans': plans})


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
                user = User.objects.get(email=form.cleaned_data['email'])
            except User.DoesNotExist:
                user = None

            # If user exists
            if user is not None:
                # Create and send token
                Token.objects.create_and_send(email_address=user.primary_email, purpose='login', next_page=next_page)
                # Create success message
                messages.success(request, 'Wir haben dir einen Anmeldelink per E-Mail geschickt.'.format(user.email))
                # Redirect to this page
                return redirect('login')

    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form, 'next': next_page})


def token_verification_view(request, code):
    """
    Checks tokens and performs corresponding action.
    """
    # Get token
    try:
        token = Token.objects.get(code=code)
    except Token.DoesNotExist:
        messages.error(request, 'Der Link ist ungültig.')
        return redirect('login')

    # Check if token is valid
    if not token.is_valid():
        messages.error(request, 'Der Link ist abgelaufen.')
        return redirect('login')

    # Do login
    if token.purpose == 'login':
        # Get user
        user = authenticate(code=code)
        # If authentication is successful, log user in
        if user is not None:
            login(request, user)
            messages.success(request, 'Du bist eingeloggt.')
            # Handle next parameter
            next_page = request.GET.get('next', None)
            if next_page is not None:
                return redirect(next_page)
            # Redirect user to login home otherwise
            return redirect('subscription_list')

    # Do email verification
    elif token.purpose == 'verification':
        token.email_address.verify()
        token.delete()
        messages.success(request, 'Die E-Mail-Adresse wurde bestätigt.')
        # Redirect to email address list
        return redirect('email_address_list')

    messages.error(request, 'Der Link ist ungültig.')
    return redirect('login')


@login_required(redirect_field_name=None)
def logout_view(request):
    """
    Logs a user out and redirects her to the login page.
    """
    logout(request)
    messages.success(request, 'Du wurdest abgemeldet.')
    return redirect('login')


@method_decorator(login_required, name='dispatch')
class EmailAddressListView(list.ListView):
    """
    Lists all email addresses of a user.
    """
    context_object_name = 'email_addresses'
    template_name = 'user/email_address_list.html'

    def get_queryset(self):
        """
        Returns only email addresses of the authenticated user.
        """
        return EmailAddress.objects.filter(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class EmailAddressCreateView(edit.CreateView):
    model = EmailAddress
    fields = ['email']
    success_url = reverse_lazy('email_address_list')
    template_name = 'user/email_address_create.html'

    def form_valid(self, form):
        """
        Adds logged in user to object.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Creates and sends a verification token.
        Redirects to success url.
        """
        email_address = self.object
        Token.objects.create_and_send(email_address=email_address, purpose='verification')
        return super().get_success_url()


@method_decorator(login_required, name='dispatch')
class EmailAddressDeleteView(edit.DeleteView):
    model = EmailAddress
    context_object_name = 'email_address'
    success_url = reverse_lazy('email_address_list')
    template_name = 'user/email_address_delete.html'

    def get_object(self, queryset=None):
        """
        Returns email address object if it is not the primary
        email address, owned by the current user and does exist.
        Otherwise a 404 exception is raised.
        """
        email_address_id = self.kwargs['email_address_id']
        user = self.request.user
        # Get object or raise 404
        email_address = get_object_or_404(EmailAddress, id=email_address_id, user=user)
        # Check if email address is primary
        if email_address.is_primary:
            raise Http404('Email address is primary')
        return email_address
