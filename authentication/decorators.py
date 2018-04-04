# Python imports
from functools import wraps

# Django imports
from django.shortcuts import redirect


def anonymous_required(func):
    """
    Decorator for views that checks whether the user is already
    logged in. If so, the user is requested to the restricted area.
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        #print(request.user)
        # Redirect logged in users to login home
        if hasattr(request, 'user'):
            if request.user.is_authenticated:
                return redirect('home')
        # Return function if user is anonymous
        return func(request, *args, **kwargs)
    return inner
