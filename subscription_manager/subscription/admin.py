# Django imports
from django.contrib import admin

# Application imports
from .models import Plan, Subscription

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'plan', 'end_date']

class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration', 'price']

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Plan, PlanAdmin)
