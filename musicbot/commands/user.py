import logging
import json
from prettytable import PrettyTable  # type: ignore
from click_skeleton import AdvancedGroup, add_options
import click

from musicbot import helpers
from musicbot.user import User
from musicbot.user_options import register_options, auth_options, login_options
from musicbot.admin_options import admin_options
from musicbot.admin import Admin
from musicbot.config import config

logger = logging.getLogger(__name__)


@click.group('user', help='User management', cls=AdvancedGroup)
def cli():
    pass


@cli.command('list', help='List users (admin)')
@add_options(
    helpers.output_option,
    admin_options,
)
def _list(graphql_admin, output, **kwargs):
    admin = Admin.from_auth(graphql=graphql_admin, **kwargs)
    users = admin.users()
    if output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Email", "Firstname", "Lastname", "Created at", "Updated at"]
        for u in users:
            pt.add_row([u["email"], u["user"]["firstName"], u["user"]["lastName"], u["user"]["createdAt"], u["user"]["updatedAt"]])
        print(pt)
    elif output == 'json':
        print(json.dumps(users))


@cli.command(aliases=['new', 'add', 'create'], help='Register a new user')
@add_options(
    helpers.save_option,
    register_options,
)
def register(save, email, password, **kwargs):
    user = User.register(email=email, password=password, **kwargs)
    if not user.token:
        logger.error('register failed')
        return
    if save:
        logger.info("saving user infos")
        config.configfile['musicbot']['email'] = email
        config.configfile['musicbot']['password'] = password
        config.configfile['musicbot']['token'] = user.token
        config.write()


@cli.command(aliases=['delete', 'remove'], help='Remove a user')
@add_options(auth_options)
def unregister(user):
    user.unregister()


@cli.command(aliases=['token'], help='Authenticate user')
@add_options(
    helpers.save_option,
    login_options,
)
def login(save, **kwargs):
    user = User.from_auth(**kwargs)
    print(user.token)
    if save:
        logger.info("saving user infos")
        config.configfile['musicbot']['token'] = user.token
        config.write()
