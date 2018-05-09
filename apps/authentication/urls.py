# Django imports
from django.urls import path
from django.views.generic import RedirectView

# Application imports
from .views import signup_view, login_view, logout_view, token_verification_view, home_view

# URL patterns
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('token/<email_b64>/<code>/', token_verification_view, name='token_verification'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
]
