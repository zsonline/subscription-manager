# Subscription manager

_Subscription manager_ is the subscription management system of the student newspaper “[Zürcher Studierendenzeitung](http://zs-online.ch/)”.


## Installation

### Requirements

Before installing this project check that [python](https://www.python.org/) is installed. You should also install a package manager for installing this project's dependencies. It is recommended to use [pipenv](https://pipenv.org/). Pipenv will also create a virtual environment for you, which separates this project's python environment from your system's python environment.

Make sure that your virtual environment is activated when working on this project. To activate it type `pipenv shell`. To deactivate it afterwards again type `exit`.

If you want to use this project in production, make sure you have [postgres](https://www.postgresql.org/) and [redis](https://redis.io/) installed and configured. Those are not needed for development, however.

### Dependencies

This project is based on a number of other packages. A full list can be found in [Pipfile](Pipfile). Install all packages by typing `pipenv install`.

## Getting started

1. The projects main **configuration** is stored in `settings/`. It is divided into development and production settings. Secret variables, however, are not stored in there. Instead, they are read from the environment. Either you set these values each time manually or you make use of a `.env` file. To do so copy `.env.example` to `.env` and complete it. Its content is loaded when activating the virtual environment with pipenv.

2. Make all **database migrations** by typing `python manage.py makemigrations` and apply them to the database: `python manage.py migrate`.

3. Start the **development server**: `python manage.py runserver`.


## Project structure

```
.
├── documentation
├── subscription_manager
│   ├── payment           # App: payment
│   ├── settings
│   ├── static
│   ├── subscription      # App: plan, subscription, period
│   ├── templates
│   ├── user              # App: user, email address, authentication
│   └── utils
└── tests
```

### Frontend

The frontend is written in Django's template language and [Scss](https://sass-lang.com/). Website and email templates are stored in `templates/`. Assets such as images and stylesheets are stored in `static/`.

```
static/
├── images
└── styles
```
```
templates/
├── authentication
├── includes
└── subscription
```

## Helpful links

- [Django documentation](https://docs.djangoproject.com/en/dev/)
- [Python documentation](https://docs.python.org/3/)
- [Scss documentation](http://sass-lang.com/documentation/)