from django.urls import path
from django.views.generic.base import RedirectView

from .views import SubscriptionListView, SubscriptionCreateView, SubscriptionUpdateView, SubscriptionDetailView,\
    SubscriptionCancelView, PlanListView, PeriodCreateView

urlpatterns = [
    path('bestellen/', PlanListView.as_view(), name='plan_list'),
    path('bestellen/<slug:plan_slug>/', SubscriptionCreateView.as_view(), name='subscription_create'),
    path('abos/', SubscriptionListView.as_view(), name='subscription_list'),
    path('abos/<int:subscription_id>/', SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('abos/<int:subscription_id>/bearbeiten/', SubscriptionUpdateView.as_view(), name='subscription_update'),
    path('abos/<int:subscription_id>/kündigen/', SubscriptionCancelView.as_view(), name='subscription_cancel'),
    path('abos/<int:subscription_id>/verlaengern/', PeriodCreateView.as_view(), name='period_create')
]
