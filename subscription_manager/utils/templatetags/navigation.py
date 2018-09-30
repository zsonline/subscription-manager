# Django imports
from django import template
from django.shortcuts import reverse


register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, view_name):
    """
    Tag function that compares the current url
    with the path of a given view name. If they
    are equal, the string 'active' is returned.
    Otherwise an empty string.
    """
    request = context['request']
    if reverse(view_name) == '/' and request.path != '/':
        return ''
    if reverse(view_name) in request.path:
        return 'active'
    return ''
