# Django imports
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', include('subscription_manager.landing.urls')),
    path('', include('subscription_manager.subscription.urls')),
    path('auth/', include('subscription_manager.authentication.urls')),
    path('admin/', admin.site.urls),
    path('manager/', include('subscription_manager.manager.urls'))
]
