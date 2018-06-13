# Django imports
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='plans', permanent=True), name='index'),
    path('', include('subscription_manager.subscription.urls')),
    path('auth/', include('subscription_manager.authentication.urls')),
    path('admin/', admin.site.urls)
]
