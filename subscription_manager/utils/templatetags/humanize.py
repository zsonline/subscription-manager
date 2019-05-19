from django import template

from ..language import humanize_francs, humanize_timedelta, humanize_number

register = template.Library()


@register.filter
def humanize(value, type):
    if type == 'duration':
        return humanize_timedelta(value)
    elif type == 'money':
        return humanize_francs(value)
    elif type == 'number':
        return humanize_number(value)
    return ''
