from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView


@method_decorator(staff_member_required, name='dispatch')
class ManagementListView(TemplateView):
    template_name = 'management/management_list.html'
