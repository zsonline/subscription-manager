from django.urls import reverse
from django.views.generic.base import RedirectView


class HomeRedirectView(RedirectView):
    """
    Choose the right home page for logged in and logged out users.
    """
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        """
        Choose home redirect url based on whether the user is
        authenticated or not.
        """
        if self.request.user.is_authenticated:
            return reverse('subscription_list')
        else:
            return reverse('plan_list')