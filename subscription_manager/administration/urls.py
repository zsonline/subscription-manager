from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', admin.site.urls),
    path('addresses/', views.addresses, name='addresses'),
]
