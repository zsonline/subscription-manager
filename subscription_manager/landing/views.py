# Django imports
from django.views.generic import list
from django.utils.decorators import method_decorator

# Project imports
from subscription_manager.authentication.decorators import anonymous_required
from subscription_manager.subscription.models import Plan


@method_decorator(anonymous_required, name='dispatch')
class PlanListView(list.ListView):
    model = Plan
    context_object_name = 'plans'
    template_name = 'landing/plan_list.html'
