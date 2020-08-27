# Subscription manager

_Subscription manager_ is the subscription management system of the student newspaper “[Zürcher Studierendenzeitung](http://zs-online.ch/)”.


## Installation

### Requirements

Before installing this project check that [Python](https://www.python.org/) is installed. You should also install a package manager for installing this project's dependencies. It is recommended to use [Pip](https://pypi.org/project/pip/). In order to separate this project's Python environment from your system's Python environment, use a virtual environment. You can create one by typing: `python -m venv .venv`.

Make sure that your virtual environment is activated when working on this project. To activate it type `source .venv/bin/activate`. To deactivate it afterwards again type `deactivate`.

If you want to use this project in production, make sure you have [Postgres](https://www.postgresql.org/) installed and access to a mail server such as [Postfix](http://www.postfix.org/) for sending emails. Both are not necessarily needed for development, though. Emails are not sent asynchronously. Therefore, the mail server should ideally be running on the same hardware to ensure that the application feels responsive.

### Dependencies

This project is based on a number of other packages. The full list can be found in [requirements.txt](requirements.txt). Install all packages in your environment by typing `pip install -r requirements.txt`.

## Getting started

1. The project's main **configuration** is stored in `settings/`. It is divided into development and production settings. Secret variables, however, are not stored in there. Instead, they are read from the environment. Either you set these values each time manually or you make use of a `.env` file. To do so copy `.env.example` to `.env` and complete it. Its content is loaded when running the application.

2. Make all **database migrations** by typing `python manage.py makemigrations` and apply them to the database: `python manage.py migrate`. You can optionally load some default data into the database, such as the default subscription plans: `python manage.py loaddata plans`.

3. Start the **development server**: `python manage.py runserver`.


## Project structure

```
.
├── scripts               # Deployment scripts
└── subscription_manager
    ├── administration    # App: administration
    ├── payment           # App: payment
    ├── settings
    ├── static
    ├── subscription      # App: plan, subscription, period
    ├── templates
    ├── user              # App: user, email address, authentication
    └── utils
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
├── administration
├── email
├── layout
├── subscription
└── user
```

## Helpful links

- [Django documentation](https://docs.djangoproject.com/en/dev/)
- [Python documentation](https://docs.python.org/3/)
- [Scss documentation](http://sass-lang.com/documentation/)
