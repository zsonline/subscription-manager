# Django imports
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('subscription_manager.authentication.urls')),
    path('', include('subscription_manager.subscription.urls'))
]
