import calendar
import datetime
import re

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, TemplateView, View
from django.utils import timezone

from subscription_manager.payment.models import Payment
from subscription_manager.subscription.models import Subscription, Period
from subscription_manager.subscription.admin import ActiveSubscriptionResource

@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class AdministrationHomeView(TemplateView):
    """
    Administration overview page containing key statistics and links
    to maintenance sub pages.
    """
    template_name = 'administration/administration_home.html'

    def get_context_data(self, **kwargs):
        """
        Adds number of active subscriptions to the context.
        """
        kwargs['active_subscriptions'] = Subscription.objects.filter(is_active=True).count()

        return super().get_context_data(**kwargs)


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class AdministrationPaymentListView(ListView):
    """
    Lists all unpaid payments, which then can be confirmed.
    """
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
    Exports active subscriptions' addresses as .csv,
    .ods, and .xlsx documents.
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


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class AdministrationStatisticsView(TemplateView):
    """
    Displays statistics data, consumed from the statistics data view,
    in charts.
    """
    template_name = 'administration/administration_statistics.html'


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
@method_decorator(cache_page(24*60*60), name='dispatch')
class AdministrationStatisticsDataView(View):
    """
    Returns statistics data in JSON format.
    """
    lower_bound_date = datetime.date.min
    upper_bound_date = datetime.date.max

    def get(self, request, *args, **kwargs):
        """
        Returns a JSON response containing all the statistics data
        of the requested time frame. If an error occurs, a json response
        containing only and error field is returned.
        """
        # Validate parameters
        try:
            start_year, start_month, end_year, end_month = self.validate_parameters(request)
        except ValidationError as e:
            return JsonResponse({
                'error': e.message
            })

        # Store the lower and upper bound of subscription periods in order to
        # not unnecessarily query the database
        periods = Period.objects.filter(start_date__isnull=False, end_date__isnull=False).order_by('start_date')
        if periods is not None:
            self.lower_bound_date = periods.first().start_date
            self.upper_bound_date = periods.last().end_date

        # Get data
        data_list_of_dicts = self.get_data(start_year, start_month, end_year, end_month)

        # Rearrange data
        data_dict_of_lists = {k: [dic[k] for dic in list(data_list_of_dicts.values())] for k in list(data_list_of_dicts.values())[0]}
        data_dict_of_lists['time'] = list(data_list_of_dicts.keys())

        return JsonResponse(data_dict_of_lists)

    def validate_parameters(self, request):
        """
        Checks whether the start and end parameter are in a valid
        format. If they are, it trims them to the period in which
        subscriptions exist.
        """
        start_arg = request.GET.get('start')
        end_arg = request.GET.get('end')

        if start_arg is None or end_arg is None:
            raise ValidationError('Start and end parameters need to be specified')

        # Validate start parameter
        matches = re.match('^(\d\d\d\d)-(\d\d)$', start_arg)
        if matches is None:
            raise ValidationError('Invalid start parameter')
        start_year = int(matches.groups()[0])
        start_month = int(matches.groups()[1])

        # Validate end parameter
        matches = re.match('^(\d\d\d\d)-(\d\d)$', end_arg)
        if matches is None:
            raise ValidationError('Invalid end parameter')
        end_year = int(matches.groups()[0])
        end_month = int(matches.groups()[1])

        # Start date must be before end date
        if start_year > end_year or (start_year == end_year and start_month >= end_month):
            raise ValidationError('Start date must be before end date')

        return start_year, start_month, end_year, end_month

    def get_data(self, start_year, start_month, end_year, end_month):
        """
        Loops over each month, gathers the relevant data and
        arranges it into a dictionary.
        """
        data = dict()

        if start_year == end_year:
            year = start_year
            for month in range(start_month, end_month + 1):
                data.update(self.get_data_by_month(year, month))
        else:
            for year in range(start_year, end_year + 1):
                if year == start_year:
                    for month in range(start_month, 12 + 1):
                        data.update(self.get_data_by_month(year, month))
                elif year == end_year:
                    for month in range(1, end_month + 1):
                        data.update(self.get_data_by_month(year, month))
                else:
                    for month in range(1, 12 + 1):
                        data.update(self.get_data_by_month(year, month))

        return data

    def get_data_by_month(self, year, month):
        """
        Returns a dictionary containing the aggregated values of the
        requested month.
        """
        if self.lower_bound_date.year > year or (self.lower_bound_date.year == year and self.lower_bound_date.month > month) \
                or self.upper_bound_date.year < year or (self.upper_bound_date.year == year and self.lower_bound_date.month < month):
            # If request month is out of range, return zero values.
            return {
                '{} {}'.format(calendar.month_abbr[month], year % 100): {
                    'active': 0,
                    'new': 0,
                    'renewed': 0,
                    'expired': 0,
                }
            }

        return {
            '{} {}'.format(calendar.month_abbr[month], year % 100): {
                'active': Subscription.objects.get_active_by_month(year, month).count(),
                'new': Subscription.objects.get_new_by_month(year, month).count(),
                'renewed': Subscription.objects.get_renewed_by_month(year, month).count(),
                'expired': Subscription.objects.get_expired_by_month(year, month).count() + Subscription.objects.get_canceled_by_month(year, month).count(),
            }
        }
