# Django imports
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('subscription_manager.administration.urls')),
    path('auth/', include('subscription_manager.authentication.urls')),
    path('', include('subscription_manager.subscription.urls'))
]
