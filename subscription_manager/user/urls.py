# Django imports
from django.urls import path

# Application imports
from .views import signup_view, login_view, logout_view, token_verification_view, EmailAddressListView,\
    EmailAddressCreateView, EmailAddressDeleteView, email_set_primary_view, email_send_verification_view

# URL patterns
urlpatterns = [
    path('auth/signup/', signup_view, name='signup'),
    path('auth/login/', login_view, name='login'),
    path('auth/token/<uuid:code>/', token_verification_view, name='token_verification'),
    path('auth/logout/', logout_view, name='logout'),
    path('account/email/', EmailAddressListView.as_view(), name='email_address_list'),
    path('account/email/create/', EmailAddressCreateView.as_view(), name='email_address_create'),
    path('account/email/<int:email_address_id>/send_verification/', email_send_verification_view, name='email_address_send_verification'),
    path('account/email/<int:email_address_id>/set_primary/', email_set_primary_view, name='email_address_set_primary'),
    path('account/email/<int:email_address_id>/delete/', EmailAddressDeleteView.as_view(), name='email_address_delete')
]
