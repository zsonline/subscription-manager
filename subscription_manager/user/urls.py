# Django imports
from django.urls import path

# Application imports
from .views import signup_view, login_view, logout_view, token_verification_view

# URL patterns
urlpatterns = [
    path('auth/signup/', signup_view, name='signup'),
    path('auth/login/', login_view, name='login'),
    path('auth/token/<code>/', token_verification_view, name='token_verification'),
    path('auth/logout/', logout_view, name='logout')
]
