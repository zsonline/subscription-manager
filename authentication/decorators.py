# Python imports
from functools import wraps

# Django imports
from django.shortcuts import HttpResponseRedirect
from django.conf import settings


def anonymous_required(func):
    """
    Decorator for views that checks whether the user is already
    logged in. If so, the user is requested to the restricted area.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        # Redirect logged in users to login home
        if hasattr(request, 'user'):
            if request.user.is_authenticated:
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        # Return function if user is anonymous
        return func(request, *args, **kwargs)
    return inner
