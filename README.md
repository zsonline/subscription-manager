# Subscription manager

_Subscription manager_, also called ZS AVS internally (short for ‘Abonnements-Verwaltungssystem’), is the subscription management system of the student newspaper ‘[Zürcher Studierendenzeitung](http://zs-online.ch/)’.


## Installation

### Requirements

Before installing this project, check whether [Python](https://www.python.org/) and [Node.js](https://nodejs.org/) are installed. If not, do so. You should also install their package managers if they are not already included. It is recommended to use [pipenv](https://pipenv.org/) for Python and [NPM](https://www.npmjs.com/) for Node.js.

Pipenv will also create a virtual environment for you, which separates this project's environment from your system's environment. To activate your created virtual environment type `pipenv shell`. To deactivate it afterwards again type `exit`. Make sure that the virtual environment is activated when working on this project.

### Dependencies

This project depends on other software. In general, Python packages are needed for the backend and Node.js packages for the frontend. However, there are exceptions such as Django, which is used for backend and frontend.

#### Pip packages

The following Python packages are needed:

- [Django](https://pypi.org/project/Django/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install these by typing `pipenv install`.

#### NPM packages

The following Node.js packages are needed:

- [gulp](https://www.npmjs.com/package/gulp)
- [gulp-sass](https://www.npmjs.com/package/gulp-sass)
- [gulp-shell](https://www.npmjs.com/package/gulp-shell)
- [gulp-sourcemaps](https://www.npmjs.com/package/gulp-sourcemaps)

Install these by typing `npm install`.


## Getting started

1. The projects main **configuration** is stored in `settings/`. Secret variables, however, are not stored in there. Instead, they are read from the environment. Either you set these values each time manually or you make use of a `.env` file. To do so copy `.env.example` to `.env` and complete it.

2. Make all **database migrations** by typing `python manage.py makemigrations` and apply them to the database: `python manage.py migrate`.

3. Start the **development server**: `python manage.py runserver`. Also run Gulp by typing `gulp`. Gulp handles the project's frontend assets (i.e. compiles `.scss` files).


## Project structure

```
.
├── subscription_manager
    ├── authentication    # App: Token authentication, login
    ├── core
        ├── settings      # Development, testing and production settings
        ├── urls.py       # Primary urls
        └── wsgi.py
    ├── payment           # App: Payment
    ├── static            # Static assets (images, styles and scripts)
    ├── subscription      # App: Subscription
    ├── templates         # HTML templates
    ├── tests             # Test cases
    ├── user              # App: Custom user model
    └── utils             # Utilities
├── gulpfile.js           # Gulp configuration
├── manage.py
├── package.json          # NPM configuration
├── README.md
└── requirements.txt      # pip packages
```


## Configuration

The configuration is stored in `settings/` where it is divided into development, production and testing settings.

```
settings/
├── base.py          # Base settings (imported by all other files)
├── development.py   # Development settings
├── production.py    # Production settings
└── testing.py       # Testing settings
```

Secret variables that should not be added to git have to be set directly in the environment. From there, the values can be read by the application. In order to avoid setting them each time, you can add the variables to a `.env` file. Its content is added to the environment when starting the application. An empty `.env` file is provided as `.env.example`.

```
SECRET_KEY=
```


## Frontend

The frontend is written in Django's template language and [Sass](https://sass-lang.com/). Files related to the frontend are stored in `static/` and `templates/`.

Assets are stored in `static/` (in particular stylesheets in `static/stylesheets/`, images in `static/scripts/`, etc.).

```
static/
├── images
├── scripts
└── styles
    └── scss
```

HTML templates are stored in `templates/`. It is further divided into subdirectories, one for each application. The folder `includes/` contains all snippets that can be included in other template files.

```
templates/
├── authentication
├── includes
└── subscription
```

### Styles

The stylesheets are written in [Sass](https://sass-lang.com/). The `.scss` files are stored in subdirectories in `stylesheets/scss/`. They are compiled into its parent directory `stylesheets/`.

```
styles/
├── scss
    ├── base         # General styles, variables
    ├── components   # Form, button, link, ...
    ├── layout       # Header, footer, pages
    ├── utils        # Mixins
    ├── vendors      # Reset
    └── main.scss    # Imports all used styles
└── main.css
```

The `.scss` files are  compiled with Gulp (the tasks are configured in `gulpfile.js`). Simply run `gulp styles`. Gulp can also watch for changes and compile each time it detects one: `gulp styles:watch`.

### Scripts

To be written.


## Contributors

To be added.


## Helpful links

- [Python documentation](https://docs.python.org/3/)
- [Pipenv documentation](https://docs.pipenv.org/)
- [Django documentation](https://docs.djangoproject.com/en/dev/)
- [Sass documentation](http://sass-lang.com/documentation/)
- [Gulp documentation](https://gulpjs.com/)
