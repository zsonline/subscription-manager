import csv

# Django imports
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path

# Application imports
from .models import Plan, Subscription

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'plan', 'end_date']
    change_list_template = 'subscription/subscription_admin_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('export/', self.export_active_as_csv),
        ]
        return new_urls + urls

    def export_active_as_csv(self, request):
        """
        Exports all active subscriptions as
        CSV document.
        """
        # Initialise CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="zs_subscriptions.csv"'
        # Fetch all subscriptions
        subscriptions = Subscription.objects.all()
        # Write header row
        writer = csv.writer(response)
        writer.writerow(['last_name', 'first_name', 'title', 'address_line_1', 'address_line_2', 'city', 'postcode'])
        # Add each active subscription to file
        for subscription in subscriptions:
            if subscription.is_active():
                writer.writerow([
                    subscription.user.last_name,
                    subscription.user.first_name,
                    '',
                    subscription.address_line_1,
                    subscription.address_line_2,
                    subscription.city,
                    subscription.postcode
                ])
        return response


class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration', 'price']

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Plan, PlanAdmin)
