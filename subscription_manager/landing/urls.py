# Django imports
from django.urls import path
from django.views.generic import TemplateView

# Application imports
from .views import PlanListView

# URL patterns
urlpatterns = [
    path('', PlanListView.as_view(), name='index'),
]
