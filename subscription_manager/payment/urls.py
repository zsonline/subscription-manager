# Django imports
from django.urls import path

# Application imports
from .views import PaymentCreateView

# URL patterns
urlpatterns = [
    path('abo/<int:subscription_id>/verlaengern/', PaymentCreateView.as_view(), name='payment_create')
]
