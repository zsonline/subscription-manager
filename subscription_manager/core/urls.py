# Django imports
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView, TemplateView

urlpatterns = [
    path('', include('subscription_manager.landing.urls')),
    path('', include('subscription_manager.subscription.urls')),
    path('', include('subscription_manager.payment.urls')),
    path('auth/', include('subscription_manager.authentication.urls')),
    path('admin/', admin.site.urls),
]

handler400 = TemplateView.as_view(template_name='400.html')
handler403 = TemplateView.as_view(template_name='403.html')
handler404 = TemplateView.as_view(template_name='404.html')
handler500 = TemplateView.as_view(template_name='500.html')

if settings.DEBUG:
    urlpatterns += [
        path('400/', TemplateView.as_view(template_name='400.html')),
        path('403/', TemplateView.as_view(template_name='403.html')),
        path('404/', TemplateView.as_view(template_name='404.html')),
        path('500/', TemplateView.as_view(template_name='500.html')),
    ]