# Django imports
from django.urls import path
from django.views.generic.base import RedirectView

# Project imports
from subscription_manager.subscription.views import SubscriptionListView, SubscriptionUpdateView, SubscriptionDetailView

# URL patterns
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='manager_subscription_list', permanent=True), name='manager_index'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription_list'),
    #path('subscription/add/'),
    path('subscription/<int:subscription_id>/', SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('subscription/<int:subscription_id>/edit/', SubscriptionUpdateView.as_view(), name='subscription_update'),
    #path('subscription/<int:id>/delete/')
]
