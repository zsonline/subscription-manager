from django.urls import path, include

from . import views
from .views import LoginTokenView


urlpatterns = [
    #path('', include('django.contrib.auth.urls')),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('token/', LoginTokenView.as_view(), name='verify_token'),
    path('token/<email_b64>/', LoginTokenView.as_view(), name='verify_token'),
    path('token/<email_b64>/<code>/', LoginTokenView.as_view(), name='verify_token'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
]