# Django imports
from django.urls import path

# Application imports
from .views import PlanSelection

# URL patterns
urlpatterns = [
    path('', PlanSelection.as_view(), name='index'),
    #path('abo/kaufen/<plan_slug>/', SubscriptionCreateView.as_view(), name='subscription_create')
]
