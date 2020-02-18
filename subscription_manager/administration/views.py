from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class AdministrationListView(TemplateView):
    template_name = 'administration/administration_home.html'
