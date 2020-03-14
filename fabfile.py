import datetime
import logging
import os

from fabric import task

GIT_REPOSITORY = 'https://github.com/studierendenzeitung/subscription-manager.git'
GIT_BRANCH = 'master'
PROJECT_DIR = '/srv/subscription-manager/'
PROJECT_USER = 'subscription_manager'
PROJECT_GROUP = 'subscription_manager'
LOG_DIR = '/var/log/subscription-manager/'


@task
def deploy(c):
    """
    Deploys the master branch.

    Usage: fab deploy --hosts=abo.zs-online.ch --prompt-for-passphrase --prompt-for-sudo-password
    """
    # Check whether connection can be established
    try:
        c.run('uname -s')
    except Exception:
        logging.error('Connection could not be established')
        exit()

    # File names and directory names
    version = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    deploy_path = os.path.join(PROJECT_DIR, version)
    venv_path = os.path.join(deploy_path, '.venv')
    dotenv_path = os.path.join(PROJECT_DIR, '.env')
    pid_file = os.path.join(PROJECT_DIR, 'subscription-manager.pid')

    # Check if environment variable file exists in project root
    if c.run('test -f {}'.format(dotenv_path), warn=True).failed:
        # File does not exist
        logging.error('Environment variables could not be found at {}'.format(dotenv_path))
        exit()

    # Create log files if they do not already exist
    if c.run('test -d {}'.format(LOG_DIR), warn=True).failed:
        # File does not exist
        c.sudo('mkdir -p {}'.format(LOG_DIR))
    c.sudo('chown -R {}:{} {}'.format(PROJECT_USER, PROJECT_GROUP, LOG_DIR))
    c.sudo('chmod -R 664 {}'.format(LOG_DIR))

    # Create new deployment directory
    c.sudo('mkdir {}'.format(deploy_path))

    # Check out the source code
    c.sudo('git clone --branch {} {} {}'.format(GIT_BRANCH, GIT_REPOSITORY, deploy_path))

    # Copy environment variables file to deploy path
    c.sudo('cp {} {}'.format(dotenv_path, deploy_path))

    # Temporarily own deployment folder
    c.sudo('chown -R {} {}'.format(c.user, deploy_path))

    # Create the virtualenv, activate the virtual environment, and install dependencies
    with c.prefix('cd {}'.format(deploy_path)):
        c.run('poetry install'.format(deploy_path))

        # Run management commands
        c.run('poetry run {}/manage.py check'.format(deploy_path))
        c.run('poetry run {}/manage.py migrate'.format(deploy_path))
        c.run('poetry run {}/manage.py collectstatic'.format(deploy_path))

    # Update the links to current deployment
    c.sudo('rm {}current'.format(PROJECT_DIR), warn=True)  # Will fail for the first deployment
    c.sudo('ln -s {} {}current'.format(deploy_path, PROJECT_DIR))

    # Set permissions
    c.sudo('chown -R {}:{} {}'.format(PROJECT_USER, PROJECT_GROUP, deploy_path))
    c.sudo('find {} -type d -exec chmod 755 {{}} +'.format(deploy_path))
    c.sudo('find {} -type f -exec chmod 644 {{}} +'.format(deploy_path))
    c.sudo('find {} -type f -exec chmod 755 {{}} +'.format(venv_path))

    # Kill the old worker so that supervisord starts the new one
    c.sudo('kill -TERM `cat {}`'.format(pid_file), warn=True)  # Will fail for the first deployment
