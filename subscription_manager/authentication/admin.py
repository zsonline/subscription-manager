# Django imports
from django.contrib import admin

# Application imports
from .models import Token

class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'valid_until')

admin.site.register(Token, TokenAdmin)