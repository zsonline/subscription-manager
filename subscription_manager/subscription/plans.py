class Plans:
    """
    Defines subscription plans and provides methods
    for getting the data in several formats.
    """
    # Define subscription types
    data = {
        1: {
            'name': 'Reguläres Abonnement',
            'description': 'Unser ganz normales Abonnement. Du zahlst, wir liefern. Sechs Mal jährlich schicken wir '
                           'dir Geschichten aus der Uni und ETH nach Hause.',
            'slug': 'regular',
            'price': 50,
            'duration': 12  # in months
        },
        2: {
            'name': 'ETH-Abonnement',
            'description': 'Studierende der ETH erhalten die ZS gratis. Registriere dich hierfür mit deiner '
                           'studentischen E-Mail-Adresse.',
            'slug': 'student',
            'price': 0,
            'duration': 6
        },
        3: {
            'name': 'Gönner-Abonnement',
            'description': 'Du zahlst mehr und unterstützt uns damit enorm. So können wir uns mal einen neuen '
                           'Computer anschaffen. Oder unser selbstgekochtes Weihnachtsessen aufpeppen.',
            'slug': 'patron',
            'min_price': 75,
            'duration': 12
        },
        4: {
            'name': 'Geschenk-Abonnement',
            'description': 'Alles gleich wie bei einem regulären Abonnement. Ausser, dass es nicht du erhältst, '
                           'sondern deine Beschenkte, dein Beschenkter.',
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