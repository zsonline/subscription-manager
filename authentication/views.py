# Django imports
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

# Project imports
from .models import User, LoginToken
from .forms import SignUpForm, LoginForm, TokenForm
from .decorators import anonymous_required


@anonymous_required
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save()
            if user is not None:
                # Create and send token
                token = LoginToken.objects.create(user=user)
                token.save()
                token.send()
                # Redirect to token verification
                return redirect('verify_token', email_b64=LoginToken.b64_encoded(token.user.email))
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


@anonymous_required
def login_view(request):
    next = request.GET.get('next', None)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Get user
            user = User.objects.get(email=form.cleaned_data['email'])
            if user is not None:
                # Create and send token
                token = LoginToken.objects.create(user=user)
                token.save()
                token.send()
                # Redirect to token verification
                return redirect('verify_token', email_b64=LoginToken.b64_encoded(token.user.email))
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@method_decorator(anonymous_required, name='dispatch')
class LoginTokenView(View):

    form_class = TokenForm
    template_name = 'authentication/verify_token.html'

    def get(self, request, *args, **kwargs):
        email_b64 = kwargs.get('email_b64', None)
        if email_b64 is not None:
            email = LoginToken.b64_decoded(email_b64)
        else:
            email = None
        code = kwargs.get('code', None)

        if email is not None and code is not None:
            if self.verify_token(request, email, code):
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            return redirect('verify_token', email_b64=email_b64)
        elif email is not None:
            form = self.form_class(
                initial={
                    'email': email,
                }
            )
            return render(request, self.template_name, {'form': form})
        else:
            form = self.form_class()
            return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            code = form.cleaned_data['code']
            if self.verify_token(request, email, code):
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template_name, {'form': form})

    @staticmethod
    def verify_token(request, email, code):
        user = authenticate(email=email, code=code)
        if user is not None:
            login(request, user)
            return True
        return False


@login_required
def home_view(request):
    return HttpResponse(request.user.email)
