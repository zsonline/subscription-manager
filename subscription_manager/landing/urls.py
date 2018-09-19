# Django imports
from django.urls import path

# Application imports
from .views import PlanSelection, Purchase

# URL patterns
urlpatterns = [
    path('', PlanSelection.as_view(), name='index'),
    path('abo/<plan_slug>/', Purchase.as_view(), name='purchase')
]
