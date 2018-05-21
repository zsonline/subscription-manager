# Django imports
from django.urls import path
from django.views.generic.base import RedirectView

# Project imports
from subscription_manager.subscription.views import SubscriptionListView, SubscriptionCreateView, \
    SubscriptionUpdateView, SubscriptionDetailView, SubscriptionDeleteView

# URL patterns
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='subscription_list', permanent=True), name='manager_index'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription_list'),
    path('subscription/add/', SubscriptionCreateView.as_view(), name='subscription_create'),
    path('subscription/<int:subscription_id>/', SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('subscription/<int:subscription_id>/edit/', SubscriptionUpdateView.as_view(), name='subscription_update'),
    path('subscription/<int:subscription_id>/delete/', SubscriptionDeleteView.as_view(), name='subscription_delete')
]
