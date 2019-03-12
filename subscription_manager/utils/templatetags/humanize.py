from django import template
from django.utils import timezone


register = template.Library()


@register.filter
def humanize(value, type):
    if type == 'duration':
        return humanize_timedelta(value)
    elif type == 'money':
        return humanize_francs(value)
    return ''


def humanize_timedelta(delta):
    if delta.days < 0:
        delta = timezone.now() - (timezone.now() + delta)

    years = delta.days // 365
    days = delta.days % 365

    if years == 0:
        if days == 0:
            return ''
        elif days == 1:
            return '1 Tag'
        else:
            return '{} Tage'.format(days)
    elif years == 1:
        if days == 0:
            return '1 Jahr'
        elif days == 1:
            return '1 Jahr und 1 Tag'
        else:
            return '1 Jahr und {} Tage'.format(days)
    else:
        if days == 0:
            return '{} Jahre'.format(years)
        elif days == 1:
            return '{} Jahre und 1 Tag'.format(years)
        else:
            return '{} Jahre und {} Tage'.format(years, days)


def humanize_francs(amount):
    if amount == 0:
        return 'gratis'
    else:
        return '{} Franken'.format(amount)
