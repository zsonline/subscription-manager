from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from import_export import resources
from import_export.admin import ExportMixin

from .models import Period, Plan, Subscription


class SubscriptionResource(resources.ModelResource):
    """
    Defines the data resource which can be exported.
    """
    class Meta:
        model = Subscription
        fields = ('first_name', 'last_name', 'address_line', 'additional_address_line', 'postcode', 'town')


class IsActiveListFilter(admin.SimpleListFilter):
    """
    Custom list filter which filters subscription by
    their status
    """
    title = 'Aktiv'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        """
        Filter options
        """
        return (
            ('active', 'Aktiv'),
            ('inactive', 'Inaktiv'),
        )

    def queryset(self, request, queryset):
        """
        Filter queryset based on set filter value.
        """
        exclude_pks = []

        # Loop through queryset
        for subscription in queryset:
            # Collect primary keys of instances which do not fit the filter criteria
            if self.value() == 'active' and not subscription.is_active() or \
                    self.value() == 'inactive' and subscription.is_active():
                exclude_pks.append(subscription.pk)

        # Remove collected primary keys
        return queryset.exclude(pk__in=exclude_pks)


class PeriodInline(admin.StackedInline):
    model = Period
    extra = 0
    readonly_fields = ['payment_link']

    def payment_link(self, period):
        """
        Returns a payment link if a payment exists.
        """
        if period.payment:
            url = reverse('admin:payment_payment_change', args=[period.payment.pk])
            return mark_safe('<a href="{}">{}</a>'.format(url, period.payment))

        return ''



class SubscriptionAdmin(ExportMixin, admin.ModelAdmin):
    """
    Subscription model admin
    """
    list_display = ['user', 'plan', 'is_active', 'end_date']
    list_filter = [IsActiveListFilter, 'plan']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'first_name', 'last_name', 'address_line', 'additional_address_line', 'postcode', 'town', 'country']
    resource_class = SubscriptionResource
    inlines = [PeriodInline]


class PlanAdmin(admin.ModelAdmin):
    """
    Plan model admin
    """
    list_display = ['name', 'price']


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Plan, PlanAdmin)
