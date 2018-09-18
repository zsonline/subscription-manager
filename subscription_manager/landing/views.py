# Django imports
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import detail, edit, list

# Project imports
from subscription_manager.authentication.decorators import anonymous_required
from subscription_manager.subscription.models import Plan

# Application imports
from subscription_manager.subscription.views import PlanListView

@method_decorator(anonymous_required, name='dispatch')
class PlanSelection(list.ListView):
    model = Plan
    context_object_name = 'plans'
    template_name = 'landing/plan_selection.html'

