from django.utils import timezone


def humanize_list(list, conjunction):
    """
    Converts a given list into a string by
    combining all elements to an enumeration
    with conjunction between the last two elements.
    """
    if len(list) == 0:
        return ''
    if len(list) == 1:
        return str(list[0])
    if len(list) == 2:
        return str(list[0]) + ' ' + conjunction + ' ' + list[1]
    humanized = ''
    for elem in list[:-2]:
        humanized += str(elem) + ', '
    humanized += humanize_list(list[-2:], conjunction)
    return humanized


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


def humanize_number(number):
    if number == 0:
        return 'kein'
    elif number == 1:
        return 'ein'
    elif number == 2:
        return 'zwei'
    elif number == 3:
        return 'drei'
    elif number == 4:
        return 'vier'
    elif number == 5:
        return 'fünf'
    elif number == 6:
        return 'sechs'
    elif number == 7:
        return 'sieben'
    elif number == 8:
        return 'acht'
    elif number == 9:
        return 'neun'
    elif number == 10:
        return 'zehn'
    elif number == 11:
        return 'elf'
    elif number == 12:
        return 'zwölf'
    else:
        return number

