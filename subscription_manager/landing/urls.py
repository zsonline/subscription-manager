# Django imports
from django.urls import path
from django.views.generic import TemplateView

# Application imports
from .views import PlanListView

# URL patterns
urlpatterns = [
    path('', PlanListView.as_view(), name='index'),
]

handler400 = TemplateView.as_view(template_name='400.html')
handler403 = TemplateView.as_view(template_name='403.html')
handler404 = TemplateView.as_view(template_name='404.html')
handler500 = TemplateView.as_view(template_name='500.html')
