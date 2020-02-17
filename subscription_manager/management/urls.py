from django.urls import path
from django.views.generic.base import RedirectView

from subscription_manager.subscription.views import SubscriptionExportView

urlpatterns = [
    path('exportieren/<str:format>/', SubscriptionExportView.as_view(), name='subscriptions_export'),
]
