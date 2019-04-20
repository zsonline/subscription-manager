from django.urls import path
from django.views.generic.base import RedirectView

from .views import SubscriptionListView, SubscriptionCreateView, SubscriptionUpdateView, SubscriptionDetailView,\
    SubscriptionCancelView, PlanListView

urlpatterns = [
    path('bestellen/', PlanListView.as_view(), name='plan_list'),
    path('bestellen/<slug:plan_slug>/', SubscriptionCreateView.as_view(), name='subscription_create'),
    path('abos/', SubscriptionListView.as_view(), name='subscription_list'),
    path('abo/abonnieren/<plan_slug>/', SubscriptionCreateView.as_view(), name='subscription_create1'),
    path('abo/<int:subscription_id>/', SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('abo/<int:subscription_id>/bearbeiten/', SubscriptionUpdateView.as_view(), name='subscription_update'),
    path('abo/<int:subscription_id>/kuendigen/', SubscriptionCancelView.as_view(), name='subscription_cancel')
]
