from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, *view_names):
    """
    Tag function that compares the given view names with the
    requested view name. If at least one is equal, 'active'
    is returned. Otherwise an empty string.
    """
    request = context.get('request')
    if request is None:
        return ''

    for view_name in view_names:
        if request.resolver_match.url_name == view_name:
            return 'active'
    return ''
