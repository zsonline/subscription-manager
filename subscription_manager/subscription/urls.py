# Django imports
from django.urls import path

# Application imports
from .views import list_plans, purchase_view, home_view, SubscriptionListView

# URL patterns
urlpatterns = [
    path('abos/', list_plans, name='list_plans'),
    path('abo/<slug>/', purchase_view, name='purchase'),
    path('home/', home_view, name='home'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription_list')
]
