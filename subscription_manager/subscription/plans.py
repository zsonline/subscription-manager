class Plans:
    """
    Defines subscription plans and provides methods
    for getting the data in several formats.
    """
    # Define subscription types
    data = {
        1: {
            'name': 'Reguläres Abonnement',
            'description': 'Lorem ipsum',
            'slug': 'regular',
            'price': 50,
            'duration': 12  # in months
        },
        2: {
            'name': 'ETH-Abonnement',
            'description': 'Lorem ipsum',
            'slug': 'student',
            'price': 0,
            'duration': 6
        },
        3: {
            'name': 'Gönner-Abonnement',
            'description': 'Lorem ipsum',
            'slug': 'patron',
            'min_price': 75,
            'duration': 12
        },
        4: {
            'name': 'Geschenk-Abonnement',
            'description': 'Lorem ipsum',
            'slug': 'gift',
            'price': 50,
            'duration': 12,
            'allow_different_name': True
        }
    }

    @classmethod
    def get(cls, slug):
        for _, plan in cls.data.items():
            if slug == plan['slug']:
                return plan
        return None

    @classmethod
    def slugs(cls):
        """
        Returns a list of all plan slugs.
        """
        slugs = list()
        for _, plan in cls.data.items():
            slugs.append(plan['slug'])
        return tuple(slugs)

    @classmethod
    def convert_to_choices(cls):
        """
        Converts the dictionary into a tuple of
        tuples that can be used as choices value.
        """
        choices = list()
        for _, plan in cls.data.items():
            subscription_type = (plan['slug'], plan['name'])
            choices.append(subscription_type)
        return tuple(choices)