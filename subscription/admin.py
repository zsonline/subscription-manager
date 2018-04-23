from django.contrib import admin
from .models import Subscription, SubscriptionType, Address


class SubscriptionTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'slug', 'duration', 'price')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('email_whitelist',),
        }),
    )


admin.site.register(SubscriptionType, SubscriptionTypeAdmin)
