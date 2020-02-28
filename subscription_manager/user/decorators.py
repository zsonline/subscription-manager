from functools import wraps

from django.conf import settings
from django.shortcuts import HttpResponseRedirect, redirect


def anonymous_required(func):
    """
    Decorator for views that checks whether the user is already
    logged in. If so, the user is redirected to the restricted area.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        # Redirect logged in users to login home
        if hasattr(request, 'user'):
            if request.user.is_authenticated:
                return redirect('home')
        # Return function if user is anonymous
        return func(request, *args, **kwargs)
    return inner
