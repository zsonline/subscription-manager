from django.urls import path
from django.views.generic.base import RedirectView

from subscription_manager.subscription.views import SubscriptionExportView

from .views import AdministrationListView

urlpatterns = [
    path('', AdministrationListView.as_view(), name='administration_home'),
    path('exportieren/<str:format>/', SubscriptionExportView.as_view(), name='subscriptions_export'),
]
