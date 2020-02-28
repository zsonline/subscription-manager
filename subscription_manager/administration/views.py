import re

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView, View
from django.utils import timezone

from subscription_manager.payment.models import Payment
from subscription_manager.subscription.admin import ActiveSubscriptionResource


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class AdministrationHomeView(TemplateView):
    template_name = 'administration/administration_home.html'


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class AdministrationPaymentListView(ListView):
    context_object_name = 'payments'
    template_name = 'administration/administration_payment_list.html'
    ordering = '-created_at'
    paginate_by = 10

    def get_queryset(self):
        """
        Only show unpaid payments with an amount greater than zero.
        If a query has been specified, execute it.
        """
        queryset = Payment.objects.filter(paid_at__isnull=True, amount__gt=0).select_related('period__subscription__user')

        # If a query is specified filter results for payments that have the query
        # as first name, last name or code
        user_query = self.request.GET.get('query')
        if user_query is not None and user_query != '':
            payment_codes = re.findall(r'\d+', user_query)
            queryset = queryset.filter(
                Q(pk__in=payment_codes) |
                Q(period__subscription__first_name__icontains=user_query) | Q(period__subscription__last_name__icontains=user_query) |
                Q(period__subscription__user__first_name__icontains=user_query) | Q(period__subscription__user__last_name__icontains=user_query)
            )

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset


@staff_member_required(login_url='login')
def payment_confirm(request, payment_id):
    """
    Checks whether a payment can be confirmed. If it can, it confirms
    it. Otherwise, a 404 page is shown.
    """
    payment = get_object_or_404(Payment, pk=payment_id, paid_at__isnull=True, amount__gt=0)
    payment.confirm()
    messages.success(request, 'Zahlung von {} wurde bestätigt.'.format(payment.period.subscription.user.full_name()))
    return redirect('administration_payment_list')


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class AdministrationSubscriptionExportView(View):
    """
    Supports the export of active subscriptions' addresses
    as .csv, .ods, and .xlsx documents.
    """
    format = 'csv'  # Default format is .csv

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method is called before get or post method.
        Checks if requested format is supported.
        """
        # Get format argument and check if it is supported. Otherwise,
        # raise 404 exception.
        format_arg = self.kwargs.get('format')
        if format_arg not in ['csv', 'ods', 'xlsx']:
            raise Http404()
        # Store format as class attribute
        self.format = format_arg

        return super().dispatch(request, *args, **kwargs)

    def content_type(self):
        """
        Return the format's corresponding content type.
        """
        if self.format == 'csv':
            return 'text/csv'
        elif self.format == 'ods':
            return 'application/vnd.oasis.opendocument.spreadsheet'
        elif self.format == 'xlsx':
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return ''

    def content(self):
        """
        Return the content formatted as the requested document.
        """
        if self.format == 'csv':
            return ActiveSubscriptionResource().export().csv
        elif self.format == 'ods':
            return ActiveSubscriptionResource().export().ods
        elif self.format == 'xlsx':
            return ActiveSubscriptionResource().export().xlsx
        return ''

    def get(self, request, *args, **kwargs):
        """
        Return the document as an attachement.
        """
        response = HttpResponse(
            content=self.content(),
            content_type=self.content_type()
        )
        response['Content-Disposition'] = 'attachment; filename="{}-active-subscriptions.{}"'.format(
            timezone.now().strftime('%Y-%m-%d'),
            self.format
        )
        return response
