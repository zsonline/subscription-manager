# Django imports
from django.urls import path
from django.views.generic import RedirectView

# Application imports
from .views import list_plans, purchase_view

# URL patterns
urlpatterns = [
    path('subscribe/', list_plans, name='list_plans'),
    path('subscribe/<slug>/', purchase_view, name='purchase')
]
