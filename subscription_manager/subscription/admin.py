# Python imports
import csv

# Django imports
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.urls import path

# Application imports
from .models import Plan, Subscription

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'plan']
    search_fields = ['user', 'plan', 'address_line_1', 'address_line_2', 'postcode', 'city', 'country']
    change_list_template = 'subscription/subscription_admin_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('export/', self.export_active_as_csv),
        ]
        return new_urls + urls

    @staticmethod
    @staff_member_required
    def export_active_as_csv(request):
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
        # Add each active subscription to file
        for subscription in subscriptions:
            if subscription.is_active():
                if subscription.address_line_2 is not None:
                    writer.writerow([
                        subscription.user.last_name,
                        subscription.user.first_name,
                        '',
                        subscription.address_line_2,
                        subscription.address_line_1,
                        subscription.city,
                        subscription.postcode
                    ])
                else:
                    writer.writerow([
                        subscription.user.last_name,
                        subscription.user.first_name,
                        '',
                        '',
                        subscription.address_line_1,
                        subscription.city,
                        subscription.postcode
                    ])
        return response


class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_in_months', 'price']


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Plan, PlanAdmin)
