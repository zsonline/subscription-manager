# ZS AVS

The ZS AVS (short for ‘Abonnements-Verwaltungssystem’) is a subscription management system for the student newspaper ‘[Zürcher Studierendenzeitung](http://zs-online.ch/)’.

## Installation

### Requirements

Before installing this project, check whether [Python](https://www.python.org/) and [Node.js](https://nodejs.org/) are installed. If not, do so. You should also install their package managers if they are not already included: pip and NPM, respectively.

### Virtual environment (optional)

In order to separate this project's environment from your system's python environment, create a virtual environment. To create one in this directory: `python -m venv venv`. There are also other tools for doing that, such as  [virtualenv](https://pypi.python.org/pypi/virtualenv).

To activate your created virtual environment, type `source venv/bin/activate`. To deactivate it afterwards again, type `deactivate`.

Make sure that the virtual environment is activated when working on this project. You can find further information about virtual environments in the [python documentation](https://docs.python.org/3/tutorial/venv.html).

### Dependencies

#### Pip packages

The following Python packages are needed:

- [Django](https://pypi.org/project/Django/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

You can install these by typing `pip install -r requirements.txt`.

#### NPM packages

The following Node.js packages are needed:

- [gulp](https://www.npmjs.com/package/gulp)
- [gulp-sass](https://www.npmjs.com/package/gulp-sass)
- [gulp-shell](https://www.npmjs.com/package/gulp-shell)
- [gulp-sourcemaps](https://www.npmjs.com/package/gulp-sourcemaps)

You can install these by typing `npm install`.

### Configuration

Secret variables cannot be stored in the settings. Instead, they are directly read from the environment. That is why you have to set them manually in the `.env` file: Copy `.env.example` to `.env` and complete it.

### Database migrations

Make all migrations by typing `python manage.py makemigrations` and apply them to the database: `python manage.py migrate`.

### Start the server

That is it. You can now start the development server: `python manage.py runserver`.


## Project structure

To be written.


## Configuration

The configuration is stored in two places: the `settings/` directory and a `.env` file.

### `settings/`

Configuration values that do not change and can be public should be stored in the appropriate settings file in `settings/`.

```
settings/
├── base.py          # Base settings (imported by all other files)
├── development.py   # Development settings
├── production.py    # Production settings
└── testing.py       # Testing settings
```

### `.env`

Configuration values that should remain secret (and not be pushed to github) have to be added directly to the environment. In order to avoid doing this each time, you can simply add the variables to the `.env` file. It is read by the application at start, which then adds the values to the environment.

```
SECRET_KEY=
```

## Frontend

### Dependencies

The frontend is written in django's own template language. It is included in django itself. Therefore, no additional packages have to be installed for templating.

The stylesheets, however, are written in [sass](https://sass-lang.com/), which depends on additional software. Because no bundler or task runner is currently included in this repository, you have to install one manually for yourself. Before doing that, though, check whether your editor or IDE has built-in tools or plugins which can compile the sass files.

### Directories

Files related to the frontend are stored in two directories: `static/` and `templates/`.

Assets are stored in `static/` (in particular stylesheets in `static/stylesheets/`, images in `static/scripts/`, etc.).

```
static/
├── images
├── scripts
└── styles
    └── scss
```

In `templates/` all template files are stored. It is further divided into subdirectories, one for each application. In addition, `includes/` contains all snippets that can be included in other template files.

```
templates/
├── authentication
│   ├── emails
├── includes
└── subscription
```

### Styles

The stylesheets are written in [sass](https://sass-lang.com/). The `.scss` files are stored in subdirectories in `static/stylesheets/scss/`. They should be compiled into its parent directory `static/stylesheets/` in order to keep the assets clearly structured. The main (and currently only) stylesheet is called `main.css`.

## Helpful links

- [Django documentation](https://docs.djangoproject.com/en/2.0/)
- [Python documentation](https://docs.python.org/3/)
- [Sass documentation](http://sass-lang.com/documentation/)
