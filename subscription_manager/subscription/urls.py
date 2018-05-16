# Django imports
from django.urls import path
from django.views.generic import RedirectView

# Application imports
from .views import list_subscription_types_view, purchase_view

# URL patterns
urlpatterns = [
    path('subscribe/', list_subscription_types_view, name='list_subscription_types'),
    path('subscribe/<slug>/', purchase_view, name='purchase')
]
