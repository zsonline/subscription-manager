# Django imports
from django.urls import path

# Application imports
from .views import signup_view, login_view, logout_view, token_verification_view, EmailAddressListView,\
    EmailAddressCreateView, EmailAddressDeleteView, email_set_primary_view, email_send_verification_view

# URL patterns
urlpatterns = [
    path('registrieren/', signup_view, name='signup'),
    path('anmelden/', login_view, name='login'),
    path('token/<uuid:code>/', token_verification_view, name='token_verification'),
    path('abmelden/', logout_view, name='logout'),
    path('konto/email/', EmailAddressListView.as_view(), name='email_address_list'),
    path('konto/email/neu/', EmailAddressCreateView.as_view(), name='email_address_create'),
    path('konto/email/<int:email_address_id>/verifizieren/', email_send_verification_view, name='email_address_send_verification'),
    path('konto/email/<int:email_address_id>/primär/', email_set_primary_view, name='email_address_set_primary'),
    path('konto/email/<int:email_address_id>/entfernen/', EmailAddressDeleteView.as_view(), name='email_address_delete')
]
