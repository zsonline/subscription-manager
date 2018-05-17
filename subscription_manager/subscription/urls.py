# Django imports
from django.urls import path
from django.views.generic import RedirectView

# Application imports
from .views import SubscriptionTypeList, purchase_view

# URL patterns
urlpatterns = [
    path(
        'subscribe/',
        SubscriptionTypeList.as_view(template_name='subscription/subscription_type_list.html'),
        name='subscription_type_list'
    ),
    path('subscribe/<slug>/', purchase_view, name='purchase')
]
