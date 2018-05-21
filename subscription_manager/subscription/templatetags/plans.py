# Django imports
from django import template

# Application imports
from ..plans import Plans


register = template.Library()


@register.simple_tag
def plan_name(slug):
    """
    Tag function that returns the plan name for
    a given slug.
    """
    return Plans.get(slug)['name']


@register.simple_tag
def humanize_months(months):
    if months % 12 == 0:
        years = int(months / 12)
        if years == 1:
            return '{} Jahr'.format(years)
        return '{} Jahre'.format(years)
    else:
        if months == 1:
            return '{} Monat'.format(months)
        return '{} Monate'.format(months)
