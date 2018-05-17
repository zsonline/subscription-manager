# Define subscription types
plans = {
    1: {
        'name': 'Abonnement',
        'description': 'Lorem ipsum',
        'slug': 'regular',
        'price': 50
    },
    2: {
        'name': 'ETH-Abonnement',
        'description': 'Lorem ipsum',
        'slug': 'student',
        'price': 50
    },
    3: {
        'name': 'Gönner-Abonnement',
        'description': 'Lorem ipsum',
        'slug': 'patron',
        'min_price': 75
    },
    4: {
        'name': 'Geschenk-Abonnement',
        'description': 'Lorem ipsum',
        'slug': 'gift',
        'price': 50
    }
}


def convert_to_choices():
    """
    Converts the dictionary into a tuple of
    tuples that can be used as choices value.
    """
    choices = list()
    for _, plan in plans.items():
        subscription_type = (plan['slug'], plan['name'])
        choices.append(subscription_type)
    return tuple(choices)
