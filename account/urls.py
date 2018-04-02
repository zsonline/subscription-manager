from django.urls import path, include

from . import views


urlpatterns = [
    #path('', include('django.contrib.auth.urls')),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('token/<uid>/<key>/', views.verify_token, name='verify_token')
]