# Django imports
from django.urls import path
from django.views.generic.base import RedirectView

# Application imports
from .views import plan_list_view, purchase_view, SubscriptionListView, SubscriptionCreateView, \
    SubscriptionUpdateView, SubscriptionDetailView, SubscriptionCancelView, PlanListView

# URL patterns
urlpatterns = [
    #path('subscriptions/', plan_list_view, name='plans'),
    #path('subscription/<plan_slug>/', purchase_view, name='purchase'),
    path('home/', RedirectView.as_view(pattern_name='subscription_list', permanent=True), name='login_index'),
    path('abo/', SubscriptionListView.as_view(), name='subscription_list'),
    path('abo/kaufen/', PlanListView.as_view(), name='plan_list'),
    path('abo/kaufen/<plan_slug>/', SubscriptionCreateView.as_view(), name='subscription_create'),
    path('abo/<int:subscription_id>/', SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('abo/<int:subscription_id>/bearbeiten/', SubscriptionUpdateView.as_view(), name='subscription_update'),
    path('abo/<int:subscription_id>/kuendigen/', SubscriptionCancelView.as_view(), name='subscription_cancel')
]
