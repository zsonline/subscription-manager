# Django imports
from django.urls import path

# Application imports
from .views import plan_list_view, purchase_view

# URL patterns
urlpatterns = [
    path('subscriptions/', plan_list_view, name='plans'),
    path('subscription/<plan_slug>/', purchase_view, name='purchase')
]
