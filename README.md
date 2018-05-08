# ZS AVS

The ZS AVS (short for ‘Abonnements-Verwaltungssystem’) is a subscription management system for the student newspaper ‘[Zürcher Studierendenzeitung](http://zs-online.ch/)’.

## Installation

### Requirements

Before installing this project, check whether [python](https://www.python.org/) (3.6) is installed. If not, do so.

### Virtual environment

It is recommended to create a virtual environment in order to separate this project's environment from your system's python environment. To create a virtual environment in this directory: `python -m venv {project_dir}/venv`. There are also other tools for doing that, such as  [virtualenv](https://pypi.python.org/pypi/virtualenv).

To activate your created virtual environment, type `source {project_dir}/venv/bin/activate`. To deactivate it afterwards again, type `deactivate`.

Make sure that the virtual environment is activated when installing or uninstalling packages regarding this project. You can find further information about virtual environments in the [python documentation](https://docs.python.org/3/tutorial/venv.html).

### Dependencies

After setting up your virtual environment, you need to install this project's dependencies, namely the following packages:

- Django (2.0.3)
- pytz (2018.3)
- python-dotenv (0.8.2)

You can install these by typing `pip install -r {project_dir}/requirements.txt`.

### Database migrations

Lastly, make all migrations by typing `python manage.py makemigrations` and apply them to the database: `python manage.py migrate`. Django is configured to store the data as a sqlite database in `{project_dir}/db.sqlite3`.

That is it. You are all done.

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

## Start the server

```
python manage.py runserver
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
