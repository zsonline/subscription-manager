from django.urls import path

from .views import AdministrationHomeView, AdministrationStatisticsView, AdministrationStatisticsDataView,\
    AdministrationPaymentListView, AdministrationSubscriptionExportView, payment_confirm

urlpatterns = [
    path('', AdministrationHomeView.as_view(), name='administration_home'),
    path('exportieren/<str:format>/', AdministrationSubscriptionExportView.as_view(), name='administration_subscription_export'),
    path('zahlungen/', AdministrationPaymentListView.as_view(), name='administration_payment_list'),
    path('zahlungen/<int:payment_id>/bestätigen/', payment_confirm, name='administration_payment_confirm'),
    path('statistik/', AdministrationStatisticsView.as_view(), name='administration_statistics'),
    path('statistik/daten/', AdministrationStatisticsDataView.as_view(), name='administration_statistics_data'),
]
