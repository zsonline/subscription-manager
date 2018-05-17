# Pip imports
from humanize import naturaldelta

# Django imports
from django import template
from django.shortcuts import reverse

register = template.Library()


@register.simple_tag
def active(request, view_name):
    """
    Tag function that compares the current url
    with the path of a given view name. If they
    are equal, the string 'active' is returned.
    Otherwise an empty string.
    """
    if reverse(view_name) == request.path:
        return 'active'
    return ''


@register.simple_tag
def natural_delta(value, months=True):
    """
    Tag function that provides timedelta humanization
    for templates.
    """
    return naturaldelta(value, months)