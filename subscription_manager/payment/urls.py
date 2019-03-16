from django.urls import path

from .views import PaymentCreateView

urlpatterns = [
    path('abo/<int:subscription_id>/verlaengern/', PaymentCreateView.as_view(), name='payment_create')
]
