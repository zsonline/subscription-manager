# Define subscription types
plans = {
    'regular': {
        'name': 'Abonnement',
        'description': 'Lorem ipsum',
        'price': 50
    },
    'student': {
        'name': 'ETH-Abonnement',
        'description': 'Lorem ipsum',
        'price': 50
    },
    'patron': {
        'name': 'Gönner-Abonnement',
        'description': 'Lorem ipsum',
        'min_price': 75
    },
    'gift': {
        'name': 'Geschenk-Abonnement',
        'description': 'Lorem ipsum',
        'price': 50
    }
}


def convert_to_choices():
    """
    Converts the dictionary into a tuple of
    tuples that can be used as choices value.
    """
    choices = list()
    for slug, info in plans.items():
        subscription_type = (slug, info['name'])
        choices.append(subscription_type)
    return tuple(choices)
