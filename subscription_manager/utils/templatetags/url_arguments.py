from django import template


register = template.Library()


@register.simple_tag
def url_replace_arg(request, field, value):
    """
    Creates or updates a url argument.
    """
    dictionary = request.GET.copy()
    dictionary[field] = value
    return dictionary.urlencode()
