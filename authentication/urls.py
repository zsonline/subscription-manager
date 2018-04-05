from django.urls import path

from .views import signup_view, login_view, logout_view, LoginTokenView, home_view


urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('token/', LoginTokenView.as_view(), name='verify_token'),
    path('token/<pk>/', LoginTokenView.as_view(), name='verify_token'),
    path('token/<pk>/<code>/', LoginTokenView.as_view(), name='verify_token'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
]