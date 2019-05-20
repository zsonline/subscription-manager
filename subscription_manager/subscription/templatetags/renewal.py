from django import template
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def renewal_link(subscription, user):
    if subscription.can_be_renewed_by(user):
        return mark_safe('<li><a href="{}">Verlängern</a></li>'.format(reverse('period_create', args=[subscription.id])))
    return ''
