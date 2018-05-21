# Django imports
from django.urls import path
from django.views.generic.base import RedirectView

# Project imports
from subscription_manager.subscription.views import SubscriptionListView

# URL patterns
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='manager_subscription_list', permanent=True), name='manager_index'),
    path('subscriptions/', SubscriptionListView.as_view(), name='manager_subscription_list')
]
