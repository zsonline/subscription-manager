# Django imports
from django.contrib import admin

# Application imports
from .models import LoginToken


# Model admin
class LoginTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'sent_at', 'valid_until')


# Register model and model admin
admin.site.register(LoginToken, LoginTokenAdmin)
