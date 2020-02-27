from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import EmailAddress, Token, User


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']


@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    """
    Email address model admin
    """
    list_display = ['email', 'name_field', 'is_primary']
    search_fields = ['email', 'user__first_name', 'user__last_name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user')

    def name_field(self, obj):
        return obj.user.full_name()
    name_field.short_description = 'Name'


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    """
    Token model admin
    """
    list_display = ['email_address', 'name_field', 'purpose', 'code', 'valid_until']
    search_fields = ['code', 'email_address__email', 'email_address__user__first_name', 'email_address__user__last_name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('email_address', 'email_address__user')

    def name_field(self, obj):
        return obj.email_address.user.full_name()
    name_field.short_description = 'Name'
