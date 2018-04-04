# Django imports
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

# Application imports
from .models import User, LoginToken
from .forms import SignUpForm, LoginForm, TokenForm
from .decorators import anonymous_required


@anonymous_required
def signup_view(request):
    """
    Renders or processes the signup form through which
    a user can register himself.
    """

    # For POST requests, process the form data
    if request.method == 'POST':

        form = SignUpForm(request.POST)

        if form.is_valid():

            # Save user
            user = form.save()

            # If user exists
            if user is not None:
                # Create and send token
                token = LoginToken.objects.create_and_send(user=user)
                # Redirect to token verification
                return redirect('verify_token', email_b64=LoginToken.b64_encoded(token.user.email))

            # If user does not exist, redirect to login page
            return redirect('login')

    # If it is another request, instantiate empty form
    else:
        form = SignUpForm()

    return render(request, 'authentication/signup.html', {'form': form})


@anonymous_required
def login_view(request):
    """
    Renders or processes the login form. If the data is valid,
    a token is sent and the user redirected to the token verification
    page. Otherwise, the login form is rendered.
    """

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
                token = LoginToken.objects.create_and_send(user=user)
                # Redirect to token verification
                return redirect('verify_token', email_b64=LoginToken.b64_encoded(token.user.email))

    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Logs a user out and redirects her to the login page.
    """

    logout(request)
    return redirect('login')


@method_decorator(anonymous_required, name='dispatch')
class LoginTokenView(View):
    """
    Handles token requests.
    """

    form_class = TokenForm
    template_name = 'authentication/verify_token.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests. Depending on the amount of given parameters,
        either the form is rendered or the user is tried to be logged in.
        """
        # Parse parameters
        email_b64 = kwargs.get('email_b64', None)
        if email_b64 is not None:
            email = LoginToken.b64_decoded(email_b64)
        else:
            email = None
        code = kwargs.get('code', None)

        # If email and code parameter is set
        if email is not None and code is not None:
            # Try to authenticate and log in
            if not self.authenticate_and_login(request, email, code):
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            return redirect('verify_token', email_b64=email_b64)
        # If email parameter is set
        elif email is not None:
            # Render form with email address as initial value
            form = self.form_class(
                initial={
                    'email': email,
                }
            )
            return render(request, self.template_name, {'form': form})
        # If no parameter is set
        else:
            # Render form
            form = self.form_class()
            return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests. It tries to log in a user with the
        submitted values. If it fails, the form is rendered.
        """

        form = self.form_class(request.POST)

        if form.is_valid():
            # Parse form input
            email = form.cleaned_data['email']
            code = form.cleaned_data['code']
            # Authenticate and log in
            if not self.authenticate_and_login(request, email, code):
                pass

        # If form not valid are user could not be authenticated, render form
        return render(request, self.template_name, {'form': form})

    @staticmethod
    def authenticate_and_login(request, email, code):
        """
        Tries to authenticate a user. If the authentication is
        successful, it will log him in.
        """

        # Authenticate
        user = authenticate(email=email, code=code)

        # If authentication is successful, log user in
        if user is not None:
            login(request, user)
            return True

        return False


@login_required
def home_view(request):
    """
    Login home view. For test purposes.
    """
    return HttpResponse(request.user.email)
