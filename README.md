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

You can install these by typing `pip install -r {project_dir}/requirements.txt`.

### Database migrations

Lastly, make all migrations by typing `python manage.py makemigrations` and apply them to the database: `python manage.py migrate`. Django is configured to store the data as a sqlite database in `{project_dir}/db.sqlite3`.

That is it. You are all done.

## Start the server

```
python manage.py runserver
```

## Helpful links

- [Django documentation](https://docs.djangoproject.com/en/2.0/)
- [Python documentation](https://docs.python.org/3/)
