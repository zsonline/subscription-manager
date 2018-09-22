# Django imports
from django.urls import path

# Application imports
from .views import PlanListView

# URL patterns
urlpatterns = [
    path('', PlanListView.as_view(), name='index'),
]
